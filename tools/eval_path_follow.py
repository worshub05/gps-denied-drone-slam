# Compare a flown path (ground truth) with the planned route and the obstacle map.
import sys
import os
import json
import math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from scipy.ndimage import distance_transform_edt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

bag, plan_file = sys.argv[1], sys.argv[2]
WS = os.path.expanduser('~/gpsdenied_ws')
meta = json.load(open(os.path.join(WS, 'maps', 'map_meta.json')))
occ = np.load(os.path.join(WS, 'maps', 'obstacle_map.npy'))
inf = np.load(os.path.join(WS, 'maps', 'obstacle_map_inflated.npy'))
RES, HALF = meta['res'], meta['half']
CLEAR = distance_transform_edt(~occ) * RES
plan = json.load(open(plan_file))
P = np.array(plan['waypoints_map'])

r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
gt = []
while r.has_next():
    topic, data, t = r.read_next()
    if topic == '/iris/ground_truth/odom':
        p = deserialize_message(data, Odometry).pose.pose.position
        gt.append((p.x, p.y, p.z))
gt = np.array(gt)
origin = gt[0]                       # takeoff point (drone on the ground)
xy = gt[:, :2] - origin[:2]          # world -> map frame
air = gt[:, 2] > origin[2] + 1.5
A = xy[air]


def seg_dist(q, a, b):
    ab = b - a
    t = np.clip(np.dot(q - a, ab) / max(np.dot(ab, ab), 1e-9), 0, 1)
    return np.linalg.norm(q - (a + t * ab))


xt = np.array([min(seg_dist(q, P[k], P[k + 1]) for k in range(len(P) - 1)) for q in A])
cells = np.clip(np.floor((A + HALF) / RES).astype(int), 0, occ.shape[0] - 1)
clear = CLEAR[cells[:, 0], cells[:, 1]]
goal_err = np.linalg.norm(xy[-1] - P[-1])
print(f"airborne samples: {len(A)}")
print(f"distance from planned route: mean {xt.mean():.2f} m, max {xt.max():.2f} m")
print(f"real clearance from obstacles: min {clear.min():.2f} m (planned min was set by the planner)")
print(f"landing point vs goal: {goal_err:.2f} m")

img = np.zeros(occ.shape)
img[inf] = 0.35
img[occ] = 1.0
fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(img.T, origin='lower', extent=[-HALF, HALF, -HALF, HALF], cmap='Greys', vmin=0, vmax=1)
ax.plot(P[:, 0], P[:, 1], 'b-o', ms=4, lw=2, label='planned route')
ax.plot(A[:, 0], A[:, 1], color='tab:red', lw=1, label='flown (ground truth)')
ax.plot(*P[-1], 'r*', ms=14)
ax.set_xlabel('x east (m)')
ax.set_ylabel('y north (m)')
ax.set_title(f"{plan['name']}: max deviation {xt.max():.2f} m, min clearance {clear.min():.2f} m")
ax.legend(loc='lower left', fontsize=8)
fig.tight_layout()
out = os.path.join(WS, 'results', 'plots', f"day17_flown_{plan['name']}.png")
fig.savefig(out, dpi=120)
print('saved', out)
