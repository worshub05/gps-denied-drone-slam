# Day 17: flying a planned route on SLAM alone

tools/follow_path.py: corner-hold waypoint follower (from square_flight_slam.py) that reads
waypoints_px4 from a planner file; lands at the goal. GPS off, MPC_XY_VEL_MAX 2 m/s,
ground-truth geofence on (now also stops follow_path). World: outdoor_v1.
Evaluation: tools/eval_path_follow.py compares ground truth (shifted to the map frame by the
takeoff point) with the planned route and the Day 15 obstacle map.

## past_rock (follow_past_rock_01): 9.6 m planned, 6 waypoints
| Measure                         | Result            |
|---------------------------------|-------------------|
| distance from planned route     | mean 0.24 m, max 0.97 m |
| real minimum clearance          | 2.86 m (planned 3.42 m) |
| landing point vs goal           | 1.13 m            |
Deviation stayed under 1 m (vs ~1.4 m excursions on the Day 13 lawnmower).
The 1.13 m landing offset combines SLAM error, drift during descent, and ~0.2 m
map-origin uncertainty (map origin = survey takeoff point, assumed equal to this takeoff).
