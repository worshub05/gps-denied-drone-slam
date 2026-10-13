import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2 as pc2

RINGS = 16
HALF_FOV_DEG = 15.0
FIELDS = [
    PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
    PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
    PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
    PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
    PointField(name='time', offset=16, datatype=PointField.FLOAT32, count=1),
    PointField(name='ring', offset=20, datatype=PointField.UINT16, count=1),
]

class RingTimeRelay(Node):
    def __init__(self):
        super().__init__('ring_time_relay')
        self.pub = self.create_publisher(PointCloud2, '/lidar3d/points_fastlio', 10)
        self.create_subscription(PointCloud2, '/lidar3d/points', self.cb, 10)

    def cb(self, msg):
        pts = list(pc2.read_points(msg, field_names=('x', 'y', 'z', 'intensity'), skip_nans=True))
        n = len(pts)
        if n == 0:
            return
        out = []
        for i, (x, y, z, inten) in enumerate(pts):
            elev = math.degrees(math.atan2(z, math.hypot(x, y)))
            ring = int(round((elev + HALF_FOV_DEG) / (2 * HALF_FOV_DEG / (RINGS - 1))))
            ring = min(RINGS - 1, max(0, ring))
            out.append((float(x), float(y), float(z), float(inten), float(i) / n * 1e5, ring))
        self.pub.publish(pc2.create_cloud(msg.header, FIELDS, out))

def main():
    rclpy.init()
    node = RingTimeRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
