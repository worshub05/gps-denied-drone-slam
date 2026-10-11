import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction


def generate_launch_description():
    home = os.path.expanduser('~')
    world = os.path.join(home, 'gpsdenied_ws/src/drone_control/worlds/outdoor_v2.world')
    px4_dir = os.path.join(home, 'PX4-Autopilot')

    # PX4 must not load ROS plugins, so remove the ROS variables for that process only
    sim_env = dict(os.environ, GALLIUM_DRIVER='d3d12', PX4_SITL_WORLD=world)
    sim_env.pop('ROS_VERSION', None)
    sim_env.pop('ROS_DISTRO', None)

    bridge = ExecuteProcess(
        cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
        output='screen',
    )
    simulator = ExecuteProcess(
        cmd=['make', 'px4_sitl', 'gazebo-classic'],
        cwd=px4_dir,
        env=sim_env,
        output='screen',
    )
    # Wait 40 seconds for the simulator to be ready, then start the hover node
    hover = TimerAction(
        period=40.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'run', 'drone_control', 'takeoff_hover'],
            output='screen',
        )],
    )
    return LaunchDescription([bridge, simulator])
