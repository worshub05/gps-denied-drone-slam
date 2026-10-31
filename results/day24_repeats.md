# Day 24: repeat runs of the behind_wall flight, with and without east/west walls

Same route (maps/path_behind_wall.json), same map, GPS off, 2 m/s, same procedure
(full-minute simulator settle, preflight SLAM check within +/-0.3 m). Only the world changes.
outdoor_v1b = outdoor_v1 + two 3 m walls facing east/west (world x = -7 and x = 12);
the geofence adds 1 m keep-out zones around them when GPSD_WORLD=outdoor_v1b.
Raw scores: results/day24_scores.txt. Plots: results/plots/flown_follow_*.png.

| Run              | World  | Mean dev | Max dev | Min clearance | Landing vs goal |
|------------------|--------|----------|---------|---------------|-----------------|
| behind_wall_01   | v1     | 0.26 m   | 0.82 m  | 2.06 m        | 0.49 m          |
| behind_wall_02   | v1     | 0.54 m   | 1.42 m  | 1.97 m        | 0.67 m          |
| behind_wall_03   | v1     | 0.49 m   | 1.26 m  | 2.20 m        | 0.96 m          |
| behind_wall_05   | v1     | 0.96 m   | 2.54 m  | 1.60 m        | 2.69 m          |
| bw_v1b_01        | v1b    | 0.22 m   | 0.61 m  | 2.34 m        | 0.20 m          |
| bw_v1b_02        | v1b    | 0.13 m   | 0.60 m  | 2.28 m        | 0.54 m          |

| Summary (mean, range) | Original world (4)    | With walls (2)       |
|-----------------------|-----------------------|----------------------|
| mean deviation        | 0.56 m (0.26-0.96)    | 0.18 m (0.13-0.22)   |
| max deviation         | 1.51 m (0.82-2.54)    | 0.61 m (0.60-0.61)   |
| min clearance         | 1.96 m (1.60-2.20)    | 2.31 m (2.28-2.34)   |
| landing vs goal       | 1.20 m (0.49-2.69)    | 0.37 m (0.20-0.54)   |
East wall clearance in v1b: 2.69 m and 2.78 m. No geofence breach in any run.

Findings:
- All six runs reached the goal without contact. In the original world, typical deviation is
  ~0.5 m with peaks up to 2.5 m; the worst run used 0.4 m of the 2 m safety margin.
- behind_wall_05 had a clean start (SLAM error 0.04 m on the ground) and drifted in flight,
  almost entirely east-west: SLAM under-counted eastward motion (truth 10.36 m vs SLAM 7.84 m).
- With east/west walls, deviation fell ~3x (mean) and ~60% (max), and runs became consistent.
  This extends the Day 23 hover result to the full navigation task.
- The Day 18 single run (0.82 m max) was the best of the four original-world runs, not typical.
- Small samples (4 vs 2). follow_behind_wall_04 was a leftover recording and was not scored.
