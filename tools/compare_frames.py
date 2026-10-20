import sys
import bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from px4_msgs.msg import VehicleLocalPosition

r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'),
       rosbag2_py.ConverterOptions('cdr', 'cdr'))
lio, px4 = [], []
while r.has_next():
    topic, data, t = r.read_next()
    if topic == '/Odometry':
        p = deserialize_message(data, Odometry).pose.pose.position
        lio.append((t, p.x, -p.y, -p.z))  # same conversion as the bridge (to FRD)
    elif topic == '/fmu/out/vehicle_local_position':
        m = deserialize_message(data, VehicleLocalPosition)
        px4.append((t, m.x, m.y, m.z))
lt = [a[0] for a in lio]
air = [a for a in px4 if a[3] < -1.0]
step = max(1, len(air) // 12)
print("    PX4 NED (x, y, z)     |  FAST-LIO2 FRD (x, y, z)")
for a in air[::step]:
    b = lio[min(bisect.bisect_left(lt, a[0]), len(lio) - 1)]
    print(f"{a[1]:7.2f} {a[2]:7.2f} {a[3]:7.2f}  | {b[1]:7.2f} {b[2]:7.2f} {b[3]:7.2f}")
