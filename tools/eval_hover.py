# Scores a SLAM-only hover: how far the drone really drifted, and the SLAM error.
import sys
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry

bag = sys.argv[1]
r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
gt, est = [], []
while r.has_next():
    topic, data, t = r.read_next()
    if topic in ('/iris/ground_truth/odom', '/Odometry'):
        p = deserialize_message(data, Odometry).pose.pose.position
        (gt if topic == '/iris/ground_truth/odom' else est).append((t / 1e9, p.x, p.y, p.z))
gt, est = np.array(gt), np.array(est)
o = gt[0, 1:]                                  # takeoff point (on the ground)
air = gt[:, 3] > o[2] + 1.5
g = gt[air]
d = np.linalg.norm(g[:, 1:3] - o[:2], axis=1)  # true horizontal distance from takeoff point
dur = g[-1, 0] - g[0, 0]
ix = np.clip(np.searchsorted(est[:, 0], g[:, 0]), 0, len(est) - 1)
err = np.linalg.norm((g[:, 1:3] - o[:2]) - est[ix, 1:3], axis=1)
w = g[:, 0] <= g[0, 0] + 60
d60, e60 = d[w], err[w]
dx, dy = g[-1, 1] - o[0], g[-1, 2] - o[1]
print(f"{bag}: first 60 s: drift mean {d60.mean():.2f} m, max {d60.max():.2f} m | "
      f"SLAM error mean {e60.mean():.2f} m, max {e60.max():.2f} m")
print(f"{bag}: final offset from takeoff: east {dx:+.2f} m, north {dy:+.2f} m")
big = d > 1.0
when = f"{g[np.argmax(big), 0] - g[0, 0]:.0f} s after takeoff" if big.any() else "never"
print(f"{bag}: first drift beyond 1 m: {when}")
print(f"{bag}: airborne {dur:.0f} s | true drift from takeoff point: mean {d.mean():.2f} m, "
      f"max {d.max():.2f} m, at end {d[-1]:.2f} m | SLAM error: mean {err.mean():.2f} m, max {err.max():.2f} m")
