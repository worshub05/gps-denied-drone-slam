import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from nav_msgs.msg import Odometry
from px4_msgs.msg import VehicleOdometry, TimesyncStatus

NAN = float('nan')


class FastlioToPx4(Node):
    def __init__(self):
        super().__init__('fastlio_to_px4')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.offset_us = None
        self.count = 0
        self.create_subscription(TimesyncStatus, '/fmu/out/timesync_status', self.on_timesync, qos)
        self.create_subscription(Odometry, '/Odometry', self.on_odom, 10)
        self.pub = self.create_publisher(VehicleOdometry, '/fmu/in/vehicle_visual_odometry', qos)
        self.get_logger().info('fastlio_to_px4 started')

    def on_timesync(self, msg):
        self.offset_us = msg.estimated_offset

    def on_odom(self, msg):
        if self.offset_us is None:
            return
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        out = VehicleOdometry()
        now_us = self.get_clock().now().nanoseconds // 1000 - self.offset_us
        out.timestamp = now_us
        out.timestamp_sample = now_us
        out.pose_frame = VehicleOdometry.POSE_FRAME_FRD
        # FAST-LIO2 frame (x fwd, y left, z up) -> PX4 FRD (x fwd, y right, z down)
        out.position = [float(p.x), float(-p.y), float(-p.z)]
        out.q = [float(q.w), float(q.x), float(-q.y), float(-q.z)]
        out.velocity_frame = VehicleOdometry.VELOCITY_FRAME_UNKNOWN
        out.velocity = [NAN, NAN, NAN]
        out.angular_velocity = [NAN, NAN, NAN]
        out.position_variance = [0.01, 0.01, 0.01]
        out.orientation_variance = [0.01, 0.01, 0.01]
        out.velocity_variance = [NAN, NAN, NAN]
        out.quality = 100
        self.pub.publish(out)
        self.count += 1
        if self.count % 50 == 0:
            self.get_logger().info(
                f'sent {self.count}: FRD pos {out.position[0]:.2f} {out.position[1]:.2f} {out.position[2]:.2f}')


def main():
    rclpy.init()
    node = FastlioToPx4()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
