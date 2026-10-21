# Builds a 2D obstacle grid from FAST-LIO2's registered point cloud.
# Frame: FAST-LIO2 world (origin at takeoff, x east, y north, z up).
import os
import json
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
from nav_msgs.msg import OccupancyGrid, Odometry
from scipy.ndimage import binary_dilation

RES = 0.2           # m per cell
HALF = 20.0         # map covers -20..20 m in x and y
Z_MIN, Z_MAX = 0.5, 4.0   # keep points at drone height (above ground, below 4 m)
MIN_HITS = 3        # cell must be hit this many times to count as an obstacle
INFLATE_M = 2.0     # safety margin from Day 13
SELF_RADIUS = 1.0   # ignore points this close to the drone (its own rotors)
N = int(2 * HALF / RES)
OUT = os.path.expanduser('~/gpsdenied_ws/maps')


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


class ObstacleMapper(Node):
    def __init__(self):
        super().__init__('obstacle_mapper')
        self.hits = np.zeros((N, N), dtype=np.int32)
        self.scans = 0
        self.pos = None
        self.create_subscription(Odometry, '/Odometry', self.on_odom, 10)
        self.create_subscription(PointCloud2, '/cloud_registered', self.on_cloud, 10)
        self.pub = self.create_publisher(OccupancyGrid, '/obstacle_map', 1)
        self.pub_inf = self.create_publisher(OccupancyGrid, '/obstacle_map_inflated', 1)
        self.create_timer(2.0, self.publish)
        os.makedirs(OUT, exist_ok=True)
        json.dump({'res': RES, 'half': HALF, 'z_min': Z_MIN, 'z_max': Z_MAX,
                   'min_hits': MIN_HITS, 'inflate_m': INFLATE_M},
                  open(os.path.join(OUT, 'map_meta.json'), 'w'))
        self.get_logger().info('obstacle_mapper started')

    def on_odom(self, msg):
        p = msg.pose.pose.position
        self.pos = np.array([p.x, p.y, p.z])

    def on_cloud(self, msg):
        arr = pc2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True)
        try:
            pts = np.stack([np.asarray(arr['x']), np.asarray(arr['y']), np.asarray(arr['z'])], axis=1)
        except Exception:
            pts = np.array([tuple(p) for p in arr], dtype=np.float64).reshape(-1, 3)
        if self.pos is None:
            return
        pts = pts[np.linalg.norm(pts - self.pos, axis=1) > SELF_RADIUS]
        pts = pts[(pts[:, 2] > Z_MIN) & (pts[:, 2] < Z_MAX)]
        ix = np.floor((pts[:, 0] + HALF) / RES).astype(int)
        iy = np.floor((pts[:, 1] + HALF) / RES).astype(int)
        ok = (ix >= 0) & (ix < N) & (iy >= 0) & (iy < N)
        np.add.at(self.hits, (ix[ok], iy[ok]), 1)
        self.scans += 1

    def grid_msg(self, occ, stamp):
        m = OccupancyGrid()
        m.header.frame_id = 'camera_init'
        m.header.stamp = stamp
        m.info.resolution = RES
        m.info.width = N
        m.info.height = N
        m.info.origin.position.x = -HALF
        m.info.origin.position.y = -HALF
        m.data = (occ.T.astype(np.int8) * 100).flatten().tolist()
        return m

    def publish(self):
        occ = self.hits >= MIN_HITS
        inflated = binary_dilation(occ, structure=disk(int(round(INFLATE_M / RES))))
        stamp = self.get_clock().now().to_msg()
        self.pub.publish(self.grid_msg(occ, stamp))
        self.pub_inf.publish(self.grid_msg(inflated, stamp))
        np.save(os.path.join(OUT, 'obstacle_map.npy'), occ)
        np.save(os.path.join(OUT, 'obstacle_map_inflated.npy'), inflated)
        self.get_logger().info(f'scans {self.scans}, occupied cells {int(occ.sum())}')


def main():
    rclpy.init()
    rclpy.spin(ObstacleMapper())


if __name__ == '__main__':
    main()
