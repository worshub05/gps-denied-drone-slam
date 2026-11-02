#!/bin/bash
# Choose the drone model's sensor noise: normal | realistic | heavy.
# Run with the simulator stopped; the next simulator start uses it.
set -e
D=~/gpsdenied_ws/src/drone_control/models/iris
case "$1" in
  normal|realistic|heavy) cp "$D/iris_$1.sdf" "$D/iris.sdf" ;;
  *) echo "usage: $0 normal|realistic|heavy"; exit 1 ;;
esac
echo "active model: $1 | IMU noise lines: $(grep -o '<bias_mean>' $D/iris.sdf | wc -l) | lidar: $(grep -o '<stddev>[0-9.]*</stddev></noise>' $D/iris.sdf)"
