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

| 07  | filter_size_map 0.3 (was 0.5)        | 0.119943 | 0.080324 | 0.739230 |

Run 07: median improved (0.038 vs ~0.065 m) but max worsened (0.74 vs 0.40-0.48 m); RMSE unchanged.
Kept filter_size_map 0.5: fewer large jumps matters more for closed-loop flight on SLAM.
Extrinsic not tuned: lidar offset [0, 0, 0.12] is taken directly from the drone model.

Final Day 9 config: point_filter_num 4, filter_size_surf 0.5, filter_size_map 0.5, rmse ~0.12 m.
