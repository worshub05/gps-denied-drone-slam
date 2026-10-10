# Setup notes (Day 2)

## Working setup
- Ubuntu 22.04 on WSL2, ROS 2 Humble, Gazebo Classic 11.10.2
- PX4-Autopilot at ~/PX4-Autopilot, tag v1.14.3
- WSL memory: %USERPROFILE%\.wslconfig with memory=12GB, processors=10, swap=8GB

## Start the simulator
cd ~/PX4-Autopilot
export GALLIUM_DRIVER=d3d12
env -u ROS_VERSION -u ROS_DISTRO make px4_sitl gazebo-classic
# at pxh>: commander takeoff, then commander land

## Fixes that were needed
- ROS apt source pointed to "noble"; changed to "jammy"
- PX4 ubuntu.sh removed the gazebo package; reinstalled gazebo
- PX4 checkout was v1.18 beta; switched to v1.14.3 and rebuilt
- Graphics used software rendering (llvmpipe); GALLIUM_DRIVER=d3d12 uses the Windows GPU
- Known harmless noise: ALSA audio errors, "Too many subscriptions", occasional "poll timeout" at startup
- Sim runs slower than real time (RTF about 0.35) on WSL
