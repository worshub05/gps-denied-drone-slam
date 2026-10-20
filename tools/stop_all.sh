#!/bin/bash
# Stop the simulator, FAST-LIO2, bridge, relay, recorders and flight scripts.
pkill -9 -f "ros2 launch"; pkill -9 -f "ros2 run"; pkill -9 -f "ros2 bag"
pkill -9 -f square_flight; pkill -9 -f lawnmower_flight; pkill -9 -f takeoff_hover
pkill -9 -f fastlio_to_px4; pkill -9 -f lidar_ring_time_relay; pkill -9 -f fastlio; pkill -9 -f rviz2
pkill -9 -f MicroXRCEAgent; pkill -9 -f px4; pkill -9 -f gz; pkill -9 -f gazebo
echo "stopped"
