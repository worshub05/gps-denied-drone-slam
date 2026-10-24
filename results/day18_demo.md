# Day 18: end-to-end GPS-denied navigation demo

Task: fly from takeoff to a goal behind the north wall (map (0, 11), about world (1, 12)),
not visible from takeoff, using only FAST-LIO2 for position (GPS off, magnetometer off).
Pipeline: Day 15 obstacle map -> Day 16 A* planner with clearance preference ->
Day 17 waypoint follower at 2 m/s -> PX4 via the FAST-LIO2 bridge. World: outdoor_v1.
Safety: ground-truth geofence widened (x -5.5..12, y -4.5..14 world) plus keep-out zones
around the north wall and rock_1 (extent + 1 m). Sim-only safety net; never triggered.

## Result (follow_behind_wall_01): single run
| Measure                       | Result                         |
|-------------------------------|--------------------------------|
| planned route                 | 21.7 m, 10 waypoints, min clearance 2.40 m |
| waypoints reached             | all 10, in 44 s                |
| distance from planned route   | mean 0.26 m, max 0.82 m        |
| real minimum clearance        | 2.06 m                         |
| landing point vs goal         | 0.49 m                         |
| geofence / keep-out           | never triggered                |
Plot: results/plots/day18_flown_behind_wall.png
