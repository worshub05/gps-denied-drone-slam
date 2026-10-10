import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, TimesyncStatus

CMD_DO_SET_MODE = 176
CMD_ARM_DISARM = 400


class TakeoffHover(Node):
    def __init__(self):
        super().__init__('takeoff_hover')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.offset_us = None
        self.create_subscription(TimesyncStatus, '/fmu/out/timesync_status', self.on_timesync, qos)
        self.offboard_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos)
        self.setpoint_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos)
        self.command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos)
        self.counter = 0
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('takeoff_hover started, waiting for PX4 time sync')

    def on_timesync(self, msg):
        if self.offset_us is None:
            self.get_logger().info('PX4 time sync received')
        self.offset_us = msg.estimated_offset

    def now_us(self):
        ros_us = self.get_clock().now().nanoseconds // 1000
        return ros_us - self.offset_us

    def send_command(self, command, p1=0.0, p2=0.0):
        msg = VehicleCommand()
        msg.timestamp = self.now_us()
        msg.command = command
        msg.param1 = p1
        msg.param2 = p2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        self.command_pub.publish(msg)

    def tick(self):
        if self.offset_us is None:
            return
        mode = OffboardControlMode()
        mode.timestamp = self.now_us()
        mode.position = True
        mode.velocity = False
        mode.acceleration = False
        mode.attitude = False
        mode.body_rate = False
        self.offboard_pub.publish(mode)

        sp = TrajectorySetpoint()
        sp.timestamp = self.now_us()
        sp.position = [0.0, 0.0, -2.5]
        sp.yaw = 0.0
        self.setpoint_pub.publish(sp)

        self.counter += 1
        if self.counter == 20:
            self.send_command(CMD_DO_SET_MODE, 1.0, 6.0)
            self.send_command(CMD_ARM_DISARM, 1.0)
            self.get_logger().info('requested offboard mode and arm')


def main(args=None):
    rclpy.init(args=args)
    node = TakeoffHover()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
