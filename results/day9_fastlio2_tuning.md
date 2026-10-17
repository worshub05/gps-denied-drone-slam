# Day 9: FAST-LIO2 tuning runs

All runs: v4_lidar3d_run_01 replayed once at 0.5x, clean run, azimuth-based point timing.
Command: evo_ape tum <run>_gt.tum <run>_est.tum -a --t_max_diff 0.1 (SE(3) Umeyama)

| Run | Change                               | RMSE (m) | Mean (m) | Max (m) |
|-----|--------------------------------------|----------|----------|---------|
| 04  | point_filter_num 4 (baseline config)  | 0.124075 | 0.094182 | 0.475522 |
| 05  | point_filter_num 1 (keep every point) | 0.221011 | 0.174560 | 0.730675 |
| 06  | repeat of run 04                      | 0.119725 | 0.092286 | 0.399678 |

Run-to-run variation (04 vs 06): about 0.004 m RMSE.
Keeping every point is a real regression; point_filter_num stays at 4.
PX4 estimator baseline rmse: 0.080750 m.
