# Day 10: FAST-LIO2 live vs replay

Config: gps_denied_3d.yaml (point_filter_num 4, filter sizes 0.5). evo_ape -a --t_max_diff 0.1.

| Run        | Conditions                                         | RMSE (m) | Median (m) | Max (m) | Poses |
|------------|----------------------------------------------------|----------|------------|---------|-------|
| live_01    | live with Gazebo, RViz on                          | 0.177852 | 0.135247   | 0.535374 | 1061 |
| live_02    | live with Gazebo, RViz on                          | 0.189601 | 0.038635   | 0.730983 | -    |
| replay_03  | live_02 sensor data replayed at 0.5x, no Gazebo, RViz off | 0.088289 | 0.024094 | 0.416812 | 1359 |

Live odometry rate ~9.9 Hz with brief dips to ~7.5 Hz.
Same data replayed gives less than half the error, so the live degradation comes from
CPU contention (Gazebo + relay + FAST-LIO2 + RViz), not the config or the flight.
RViz was measured at ~119% CPU during replay. Next: live run with rviz:=false.
