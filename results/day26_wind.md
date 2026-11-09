# Day 26: Wind test

World: `outdoor_v1b_wind` (outdoor_v1b + Gazebo wind plugin: steady 3 m/s from the south,
variance 0.5; gusts 3 m/s mean, up to 10 m/s, from the west, starting at 180 s for 600 s).
Drone model: normal (noise-free IMU). PX4 in SLAM-only mode (GPS off).

## Hover in wind (`hover_wind`)

| Metric | Calm | Wind |
|---|---|---|
| Mean tilt | 0.10 deg | 8.35 deg (roll +5.7, pitch -5.7) |
| SLAM error (airborne) | - | mean 0.05 m, max 0.19 m |
| Drift while holding height (398 s) | 0.11-0.17 m | mean 0.14 m, max 0.65 m |
| Drift during failsafe descent | - | up to 2.18 m (downwind) |

## Behind-wall route in wind (`follow_wind_b`)

| Metric | Calm v1b (Day 24, 2 runs) | Wind |
|---|---|---|
| Mean distance from route | 0.18 m | 0.14 m |
| Max distance from route | 0.61 m | 0.53 m |
| Min real clearance | 2.31 m | 2.20 m |
| Landing vs goal | 0.37 m | 0.69 m |

Plot: `results/plots/flown_follow_wind_b.png`. Raw scores: `results/day26_scores.txt`.

## Findings

- FAST-LIO2 stayed accurate while the drone leaned about 8 deg into the wind (max error 0.19 m).
- Route following in wind was as good as in calm air (within run-to-run variation).
- The weak point is descent: the drone drifts downwind while landing (0.69 m on the route,
  up to 2.18 m in the hover failsafe landing). This is a control limitation, not a SLAM one.
- One startup attempt (`follow_wind`) failed: FAST-LIO2 diverged on the ground (positions
  ~1e14 m, PX4 xy_valid false). The preflight check caught it and the drone did not fly.
  A clean restart with a 2-minute settle worked. Discarded, not scored.

## Limitations

- Single run per test. Wind acts on the rotors only (gazebo motor model drag), not the body.
