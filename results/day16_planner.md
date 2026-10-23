# Day 16: A* path planner (offline, on the Day 15 map)

tools/astar_planner.py: 8-connected A* on the inflated map (obstacles + 2 m margin are
forbidden), with a clearance preference: cells 2.0-3.5 m from an obstacle cost up to 3x more,
so routes keep their distance where cheap. The path is then simplified into straight legs;
a shortcut is only taken if it gets no closer to obstacles than the A* route. Output:
waypoints in the map frame (x east, y north) and the PX4 frame (x east, y south, z down),
saved to maps/path_<name>.json, plus a plot in results/plots/day16_path_<name>.png.

| Test        | Goal (map) | Shortest-path version     | With clearance preference      |
|-------------|------------|---------------------------|--------------------------------|
| past_rock   | (8, -3)    | 8.6 m, clearance ~2.0 m   | 9.6 m, 6 waypoints, clearance 3.42 m |
| behind_wall | (0, 11)    | 17.8 m, clearance ~2.0 m  | 21.7 m, 10 waypoints, clearance 2.40 m |
| inside_rock | (-5, -6)   | refused                   | refused (goal inside obstacle margin) |

Why: pure shortest paths ran along the edge of the 2 m margin, threading a <1 m gap between
rock_1's and the wall's margins. With Day 13 excursions of up to ~1.4 m, that left ~0.6 m of
real clearance; the preference raises it to ~1 m on behind_wall.
Limitations: unseen areas are treated as free; behind_wall goal (world 1, 12) is outside the
Day 13 geofence and needs a wider fence for flight.
