# Simulator-only safety net: stops the flight script if ground truth leaves a safe box,
# so PX4's failsafe lands the drone. Uses ground truth because PX4's own geofence relies
# on the same SLAM estimate that may be wrong.
import subprocess
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

LIMITS = {'x_min': -5.5, 'x_max': 10.5, 'y_min': -4.5, 'y_max': 7.0}


class Geofence(Node):
    def __init__(self):
        super().__init__('gt_geofence')
        self.tripped = False
        self.create_subscription(Odometry, '/iris/ground_truth/odom', self.on_gt, 10)
        self.get_logger().info(f'geofence active: {LIMITS}')

    def on_gt(self, msg):
        p = msg.pose.pose.position
        if self.tripped or p.z < 1.0:
            return
        inside = (LIMITS['x_min'] < p.x < LIMITS['x_max'] and
                  LIMITS['y_min'] < p.y < LIMITS['y_max'])
        if not inside:
            self.tripped = True
            self.get_logger().error(
                f'GEOFENCE BREACH at x={p.x:.2f} y={p.y:.2f}, stopping flight script')
            subprocess.run(['pkill', '-9', '-f', 'square_flight|lawnmower_flight|takeoff_hover|follow_path'])


def main():
    rclpy.init()
    rclpy.spin(Geofence())


if __name__ == '__main__':
    main()
