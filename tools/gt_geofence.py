# Simulator-only safety net: stops the flight script if ground truth leaves a safe box,
# so PX4's failsafe lands the drone. Uses ground truth because PX4's own geofence relies
# on the same SLAM estimate that may be wrong.
import subprocess
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

LIMITS = {'x_min': -5.5, 'x_max': 12.0, 'y_min': -4.5, 'y_max': 14.0}
# keep-out boxes around obstacles (world frame: obstacle extent + 1 m)
EXCLUDE = {'north_wall': (-6.6, 6.2, 6.4, 9.2), 'rock_1': (4.0, 8.0, 0.0, 4.0)}


class Geofence(Node):
    def __init__(self):
        super().__init__('gt_geofence')
        self.tripped = False
        self.create_subscription(Odometry, '/iris/ground_truth/odom', self.on_gt, 10)
        self.get_logger().info(f'geofence active: {LIMITS}, keep-out: {list(EXCLUDE)}')

    def on_gt(self, msg):
        p = msg.pose.pose.position
        if self.tripped or p.z < 1.0:
            return
        inside = (LIMITS['x_min'] < p.x < LIMITS['x_max'] and
                  LIMITS['y_min'] < p.y < LIMITS['y_max'])
        hit = [n for n, (x0, x1, y0, y1) in EXCLUDE.items() if x0 < p.x < x1 and y0 < p.y < y1]
        if not inside or hit:
            self.tripped = True
            self.get_logger().error(
                f'GEOFENCE BREACH at x={p.x:.2f} y={p.y:.2f} {hit}, stopping flight script')
            subprocess.run(['pkill', '-9', '-f', 'square_flight|lawnmower_flight|takeoff_hover|follow_path'])


def main():
    rclpy.init()
    rclpy.spin(Geofence())


if __name__ == '__main__':
    main()
