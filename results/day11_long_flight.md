# Day 11: long flight (lawnmower, 2 laps) with FAST-LIO2 live

Path: 19 waypoints, 3 m altitude, area x -3..8 m, y -2..5.5 m (world), clear of all obstacles.
Ground-truth path length 159.6 m, duration 231 s. FAST-LIO2 live, rviz:=false.
Timestamps: message header stamps (converter updated; recording-time stamps gave nearly
identical results, rmse 0.293 vs 0.291 m).

## Absolute error (evo_ape -a)
| Metric | Value (m) |
|--------|-----------|
| rmse   | 0.290609  |
| mean   | 0.251141  |
| median | 0.190933  |
| max    | 0.873412  |
With scale correction (-as): scale 1.013, rmse 0.285 -> scale error ruled out.

## Error vs segment length (tools/drift_per_distance.py, position-only)
| Segment | Mean error (m) | Median (m) | Max (m) |
|---------|----------------|------------|---------|
| 10 m    | 0.510          | 0.585      | 0.963   |
| 20 m    | 0.368          | 0.333      | 0.836   |
| 40 m    | 0.298          | 0.243      | 1.012   |
| 80 m    | 0.496          | 0.575      | 0.927   |

Error does not grow with distance: bounded at ~0.3-0.5 m over 160 m.
Percent-per-distance figures are not a drift rate here (fixed error divided by length).
Caveat: small area with the same five objects always in view; FAST-LIO2 re-registers
against the same map, so drift in a larger area is untested.
Comparison: square flight live rmse 0.123 m (~25 m path).
