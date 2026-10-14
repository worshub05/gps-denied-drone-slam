import sys
import rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import Odometry

bag, out_prefix = sys.argv[1], sys.argv[2]
r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'),
       rosbag2_py.ConverterOptions('cdr', 'cdr'))
gt, est = [], []
while r.has_next():
    topic, data, stamp = r.read_next()
    if topic not in ('/iris/ground_truth/odom', '/Odometry'):
        continue
    m = deserialize_message(data, Odometry)
    p, q = m.pose.pose.position, m.pose.pose.orientation
    line = f"{stamp/1e9:.9f} {p.x} {p.y} {p.z} {q.x} {q.y} {q.z} {q.w}"
    (gt if topic == '/iris/ground_truth/odom' else est).append(line)
with open(out_prefix + '_gt.tum', 'w') as f:
    f.write('\n'.join(gt) + '\n')
with open(out_prefix + '_est.tum', 'w') as f:
    f.write('\n'.join(est) + '\n')
print(f"gt: {len(gt)}, est: {len(est)}")
