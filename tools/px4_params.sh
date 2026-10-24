#!/bin/bash
# Switch PX4 SITL between GPS-denied (SLAM) and normal GPS flight.
# Usage: tools/px4_params.sh slam | gps     (run while the simulator is running)
set -e
P=~/PX4-Autopilot/build/px4_sitl_default/bin/px4-param
case "$1" in
  slam)
    $P set EKF2_EV_CTRL 11; $P set EKF2_GPS_CTRL 0; $P set EKF2_HGT_REF 3
    $P set EKF2_EV_DELAY 50; $P set EKF2_MAG_TYPE 5; $P set MPC_XY_VEL_MAX 2.0 ;;
  gps)
    $P set EKF2_EV_CTRL 0; $P set EKF2_GPS_CTRL 7; $P set EKF2_HGT_REF 1
    $P set EKF2_EV_DELAY 0; $P set EKF2_MAG_TYPE 0; $P set MPC_XY_VEL_MAX 12.0 ;;
  *) echo "usage: $0 slam|gps"; exit 1 ;;
esac
$P save
for p in EKF2_EV_CTRL EKF2_GPS_CTRL EKF2_HGT_REF EKF2_EV_DELAY EKF2_MAG_TYPE MPC_XY_VEL_MAX; do
  $P show $p | grep "$p"
done
