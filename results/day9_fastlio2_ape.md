# Day 9: FAST-LIO2 (3D lidar + IMU) odometry vs ground truth

Bag: fastlio_run_02 (v4_lidar3d_run_01 replayed at 0.5x)
Command: evo_ape tum fastlio02_gt.tum fastlio02_est.tum -a --t_max_diff 0.1
Alignment: SE(3) Umeyama

| Metric | Value (m) |
|--------|-----------|
| max    | 0.858898  |
| mean   | 0.282216  |
| median | 0.172326  |
| min    | 0.027668  |
| rmse   | 0.348737  |
| std    | 0.204869  |

Baseline for comparison: PX4 estimator rmse 0.080750 m (results/day8_px4_estimator_ape.md).
Config: config/gps_denied_3d.yaml (lidar_type 2, scan_line 16, blind 0.3, extrinsic_T [0,0,0.12]).
Odometry poses: 485, ground truth poses: 5900.
