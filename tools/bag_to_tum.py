import sys
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry
from px4_msgs.msg import VehicleLocalPosition

bag, out_prefix = sys.argv[1], sys.argv[2]
r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'),
       rosbag2_py.ConverterOptions('cdr', 'cdr'))

gt_lines, est_lines = [], []
while r.has_next():
    topic, data, stamp = r.read_next()
    t = stamp / 1e9
    if topic == '/iris/ground_truth/odom':
        m = deserialize_message(data, Odometry)
        p, q = m.pose.pose.position, m.pose.pose.orientation
        gt_lines.append(f"{t:.9f} {p.x} {p.y} {p.z} {q.x} {q.y} {q.z} {q.w}")
    elif topic == '/fmu/out/vehicle_local_position':
        m = deserialize_message(data, VehicleLocalPosition)
        # NED -> ENU: east = y, north = x, up = -z
        est_lines.append(f"{t:.9f} {m.y} {m.x} {-m.z} 0.0 0.0 0.0 1.0")

with open(out_prefix + '_gt.tum', 'w') as f:
    f.write('\n'.join(gt_lines) + '\n')
with open(out_prefix + '_est.tum', 'w') as f:
    f.write('\n'.join(est_lines) + '\n')
print(f"gt poses: {len(gt_lines)}, estimator poses: {len(est_lines)}")
