# Day 8: PX4 estimator error vs ground truth (baseline)

Bag: v2_square_run_01 (recorded in outdoor_v1 world, two square flights)
Command: evo_ape tum run01_gt.tum run01_est.tum -a --t_max_diff 0.05
Alignment: SE(3) Umeyama (position and orientation aligned)

| Metric | Value (m) |
|--------|-----------|
| max    | 0.402589  |
| mean   | 0.069197  |
| median | 0.058964  |
| min    | 0.006729  |
| rmse   | 0.080750  |
| std    | 0.041621  |

Ground truth poses: 9382. Estimator poses: 14070.
