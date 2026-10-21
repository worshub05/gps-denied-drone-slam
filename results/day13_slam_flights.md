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

## Lawnmower (slam_lawn_01)
FAST-LIO2 estimate vs ground truth (evo_ape -a): rmse 0.734974, mean 0.659064,
median 0.666471, max 1.447125 m. True path 177.6 m in 172 s.
GPS-flown comparison (Day 11, outdoor_v1): rmse 0.29 m over 160 m.
Error over time (20 s windows, mean m): 0.74, 0.61, 0.47, 0.48, 0.55, 0.48, 0.71, 0.83, 1.33.
U-shape = steady drift spread by global alignment, accelerating in the last ~40 s.
Error vs segment length (mean/max m): 10 m 0.91/2.01, 40 m 0.60/2.09, 80 m 0.99/1.88.
True path while airborne: x -3.67..11.72, y -1.78..7.18 (planned about x -2..9, y -1..6.5).
Near miss: reached x 11.72, ~0.15 m from the east wall face (x 12). Estimate error
(up to 1.45 m) plus corner overshoot (up to ~1.5 m) pushed the drone 2.7 m beyond the plan.
Closed-loop SLAM error is ~2.5x the open-loop (GPS-flown) error on the same path.

## Lawnmower, slower (slam_lawn_02)
Change: MPC_XY_VEL_MAX 2.0 m/s (PX4 default 12.0; restore later). Safety: tools/gt_geofence.py
(ground-truth fence x -5.5..10.5, y -4.5..7.0; sim-only). No geofence breach.
FAST-LIO2 estimate vs ground truth (evo_ape -a): rmse 0.240509, mean 0.183880,
median 0.093773, max 0.947808 m. True path 158.0 m in 297 s (about 120 s on the ground).
Error over time (30 s windows, mean/max m): ground 0.09/0.09 for 0-90 s; airborne
0.17/0.70, 0.42/0.85, 0.20/0.44, 0.24/0.47, 0.31/0.95, 0.13/0.39; ground 0.09 at the end.
No growth over time (fast run rose to 1.33 m at the end).
True path while airborne: x -2.95..10.43, y -2.22..6.88. Came within 0.07 m of the
fence limit (x 10.5) and ~1.4 m of the east wall face: still ~1.4 m beyond the planned box.

## Day 13 summary
| Flight (SLAM only, GPS off) | Speed       | RMSE (m) | Max (m) | True path |
|-----------------------------|-------------|----------|---------|-----------|
| square (slam_square_01)     | default     | 0.085    | 0.387   | ~25 m     |
| lawnmower (slam_lawn_01)    | default     | 0.735    | 1.447   | 177.6 m   |
| lawnmower (slam_lawn_02)    | 2 m/s limit | 0.241    | 0.948   | 158.0 m   |
Slowing to 2 m/s cut lawnmower error by about two thirds and stopped the drift growth.
Ground time is included in these RMSE values; airborne-only figures to be computed on Day 14.
Planning rule for Week 3: keep planned paths at least 2 m from obstacles.

## Correction (Day 15)
outdoor_v1b.world was never loaded: the launch file was edited in src/ but ros2 launch used
the unchanged install/ copy, so Gazebo ran outdoor_v1.world (confirmed with gz model: wall_east
and wall_west not found, wall_1 present). All Day 12-14 flights ran in outdoor_v1.
- Day 12: the stable second hover was not caused by added walls. The first hover's east-west
  drift is real; the degeneracy explanation is plausible but untested.
- Day 13/14: the "world gained walls" caveat is void. SLAM-only and GPS-flown lawnmower runs
  used the same world, so that comparison is like-for-like.
