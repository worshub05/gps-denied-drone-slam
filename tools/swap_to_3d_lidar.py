path = '/home/shub_2605/gpsdenied_ws/src/drone_control/models/iris/iris.sdf'
block = """    <link name='lidar_link'>
      <pose>0 0 0.12 0 0 0</pose>
      <inertial>
        <mass>0.3</mass>
        <inertia><ixx>1e-5</ixx><ixy>0</ixy><ixz>0</ixz><iyy>1e-5</iyy><iyz>0</iyz><izz>1e-5</izz></inertia>
      </inertial>
      <visual name='visual'>
        <geometry><cylinder><radius>0.04</radius><length>0.06</length></cylinder></geometry>
      </visual>
      <sensor name='lidar3d' type='ray'>
        <ray>
          <scan>
            <horizontal><samples>360</samples><resolution>1</resolution><min_angle>-3.14159</min_angle><max_angle>3.14159</max_angle></horizontal>
            <vertical><samples>16</samples><resolution>1</resolution><min_angle>-0.2618</min_angle><max_angle>0.2618</max_angle></vertical>
          </scan>
          <range><min>0.3</min><max>40</max><resolution>0.01</resolution></range>
          <noise><type>gaussian</type><mean>0.0</mean><stddev>0.01</stddev></noise>
        </ray>
        <plugin name='gazebo_ros_lidar3d' filename='libgazebo_ros_ray_sensor.so'>
          <ros><namespace>/lidar3d</namespace><remapping>~/out:=points</remapping></ros>
          <output_type>sensor_msgs/PointCloud2</output_type>
          <frame_name>lidar_link</frame_name>
        </plugin>
        <always_on>1</always_on>
        <update_rate>10</update_rate>
        <visualize>false</visualize>
      </sensor>
    </link>
    <joint name='lidar_joint' type='fixed'>
      <parent>base_link</parent>
      <child>lidar_link</child>
    </joint>
"""
src = open(path).read()
start = src.find("    <link name='rplidar_link'>")
if start < 0:
    print('2D lidar block not found')
else:
    j = src.find("<joint name='rplidar_joint'", start)
    end = src.find("</joint>", j) + len("</joint>\n")
    open(path, 'w').write(src[:start] + block + src[end:])
    print('3D lidar installed')
