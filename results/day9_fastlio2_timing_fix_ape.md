# Day 9: FAST-LIO2 after per-point timing fix

Change: relay sets each point's time from its azimuth within the 0.1 s sweep
(previously from its index in the message).
Bag: fastlio_run_04 (v4_lidar3d_run_01 replayed once at 0.5x, clean run)
Command: evo_ape tum fastlio04_gt.tum fastlio04_est.tum -a --t_max_diff 0.1

| Metric | Before (run_02) | After (run_04) |
|--------|-----------------|----------------|
| max    | 0.858898        | 0.475522       |
| mean   | 0.282216        | 0.094182       |
| median | 0.172326        | 0.065673       |
| min    | 0.027668        | 0.014362       |
| rmse   | 0.348737        | 0.124075       |
| std    | 0.204869        | 0.080774       |

Odometry poses: 926 (was 485). PX4 estimator baseline rmse: 0.080750 m.
Note: run_02 may also have been affected by a replay issue, so the gain is not
attributed to the timing change alone.
