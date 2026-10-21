# Week 2 summary: trajectory accuracy (airborne only)

Method: estimate vs Gazebo ground truth, samples with ground-truth height > 1.5 m only,
SE(3) Umeyama alignment fitted on the airborne part, message header timestamps
(Day 8 PX4 baseline uses its original recording-time conversion). Plots in results/plots/.

| Run | Airborne path (m) | RMSE (m) | Mean (m) | Median (m) | Max (m) | Poses |
|-----|-------------------|----------|----------|------------|---------|-------|
| PX4 estimator, GPS on, square (Day 8) | 48.1 | 0.104 | 0.101 | 0.102 | 0.175 | 2190 |
| FAST-LIO2 bag replay, square (Day 9, run 06) | 28.2 | 0.178 | 0.150 | 0.141 | 0.414 | 304 |
| FAST-LIO2 live, square, GPS flying (Day 10) | 28.0 | 0.170 | 0.155 | 0.139 | 0.388 | 297 |
| FAST-LIO2 live, lawnmower, GPS flying (Day 11) | 154.5 | 0.309 | 0.278 | 0.277 | 0.700 | 1168 |
| SLAM only, square (Day 13) | 27.9 | 0.138 | 0.112 | 0.097 | 0.388 | 268 |
| SLAM only, lawnmower, default speed (Day 13) | 174.6 | 0.646 | 0.578 | 0.577 | 1.333 | 1345 |
| SLAM only, lawnmower, 2 m/s (Day 13) | 155.0 | 0.320 | 0.270 | 0.223 | 0.945 | 1451 |

## Takeaways
- Airborne-only scoring raises every figure versus earlier ground-inclusive numbers
  (e.g. PX4 baseline 0.081 -> 0.104 m); these airborne values supersede earlier quotes.
- Square: FAST-LIO2 0.14-0.18 m RMSE, about 1.5x PX4's GPS-aided estimate (0.104 m).
- Lawnmower (~155 m): SLAM-only flight at 2 m/s (0.320 m) matches GPS-flown FAST-LIO2
  (0.309 m). Caveat: the world gained two east/west walls between Day 11 and Day 13.
- Default speed with SLAM in the loop doubles the error (0.646 m) and caused a near miss.
- Known limits: east-west degeneracy without walls (Day 12), ~1.4 m beyond-plan excursions
  even at 2 m/s, results from single runs, small simulated world with few features.

## Correction (Day 15)
outdoor_v1b.world was never loaded: the launch file was edited in src/ but ros2 launch used
the unchanged install/ copy, so Gazebo ran outdoor_v1.world (confirmed with gz model: wall_east
and wall_west not found, wall_1 present). All Day 12-14 flights ran in outdoor_v1.
- Day 12: the stable second hover was not caused by added walls. The first hover's east-west
  drift is real; the degeneracy explanation is plausible but untested.
- Day 13/14: the "world gained walls" caveat is void. SLAM-only and GPS-flown lawnmower runs
  used the same world, so that comparison is like-for-like.
