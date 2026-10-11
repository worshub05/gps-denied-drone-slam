import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, TimesyncStatus, VehicleLocalPosition

CMD_DO_SET_MODE = 176
CMD_ARM_DISARM = 400
CMD_NAV_LAND = 21

# Positions in metres, NED frame: x forward, y right, z negative = up
WAYPOINTS = [
    (0.0, 0.0, -2.5),
    (5.0, 0.0, -2.5),
    (5.0, 5.0, -2.5),
    (0.0, 5.0, -2.5),
    (0.0, 0.0, -2.5),
]
ARRIVE_DISTANCE = 0.5


class SquareFlight(Node):
    def __init__(self):
        super().__init__('square_flight')
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.offset_us = None
        self.pos = None
        self.wp = 0
        self.counter = 0
        self.landing_sent = False
        self.create_subscription(TimesyncStatus, '/fmu/out/timesync_status', self.on_timesync, qos)
        self.create_subscription(VehicleLocalPosition, '/fmu/out/vehicle_local_position', self.on_pos, qos)
        self.offboard_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos)
        self.setpoint_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos)
        self.command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos)
        self.timer = self.create_timer(0.1, self.tick)
        self.get_logger().info('square_flight started')

    def on_timesync(self, msg):
        self.offset_us = msg.estimated_offset

    def on_pos(self, msg):
        self.pos = (msg.x, msg.y, msg.z)

    def now_us(self):
        return self.get_clock().now().nanoseconds // 1000 - self.offset_us

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

        self.counter += 1
        if self.counter == 20:
            self.send_command(CMD_DO_SET_MODE, 1.0, 6.0)
            self.send_command(CMD_ARM_DISARM, 1.0)
            self.get_logger().info('requested offboard mode and arm')

        target = WAYPOINTS[min(self.wp, len(WAYPOINTS) - 1)]
        if self.pos is not None and self.wp < len(WAYPOINTS):
            if math.dist(self.pos, target) < ARRIVE_DISTANCE:
                self.get_logger().info(f'reached waypoint {self.wp}: {target}')
                self.wp += 1
                if self.wp == len(WAYPOINTS) and not self.landing_sent:
                    self.send_command(CMD_NAV_LAND)
                    self.landing_sent = True
                    self.get_logger().info('square done, landing')

        sp = TrajectorySetpoint()
        sp.timestamp = self.now_us()
        sp.position = [float(target[0]), float(target[1]), float(target[2])]
        sp.yaw = 0.0
        self.setpoint_pub.publish(sp)


def main(args=None):
    rclpy.init(args=args)
    node = SquareFlight()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
