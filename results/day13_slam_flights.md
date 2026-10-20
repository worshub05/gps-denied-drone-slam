# Day 13: flights on SLAM alone (GPS off)

World: outdoor_v1b. PX4: EKF2_EV_CTRL 11, EKF2_GPS_CTRL 0, EKF2_HGT_REF 3, EKF2_MAG_TYPE 5.
Flight scripts: tools/square_flight_slam.py and tools/lawnmower_flight_slam.py, waypoints
converted to PX4's vision frame (x = east, y = south) so they fly the same physical paths
as the GPS baseline.

## Square (slam_square_01)
FAST-LIO2 estimate vs ground truth (evo_ape -a): rmse 0.084718, mean 0.052620,
median 0.013141, max 0.386588 m (752 estimates).
True path while airborne: x 0.66..6.41 m (span 5.75), y 0.13..6.67 m (span 6.54).
Same area as the GPS baseline square (~0.5..6.5 m), with similar corner overshoot.
Caveats: recording includes ground time before takeoff and after landing (lowers the median);
the world gained two walls since Day 10 (live, GPS flying: rmse 0.123 m in outdoor_v1),
so the improvement is not attributed to closed-loop flight alone.
