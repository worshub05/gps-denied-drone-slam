# Day 23: walls test (east-west degeneracy)

Question: does the SLAM-only east-west hover drift (Day 12) come from missing geometry?
Setup: SLAM-only hover (GPS off) with takeoff_hover, alternating worlds:
outdoor_v1 (north wall, two thin trees: little east-west constraint) and outdoor_v1b
(outdoor_v1 + two 3 m walls facing east/west at world x = -7 and x = 12).
World selected with GPSD_WORLD (launch file reads it; verified with gz model each run).
Scoring: tools/eval_hover.py (ground truth vs takeoff point; SLAM error vs ground truth).

| Run    | World      | Airborne | First 60 s max | Max drift | Beyond 1 m | Final offset | SLAM err max |
|--------|------------|----------|----------------|-----------|------------|--------------|--------------|
| v1_a   | no walls   | 205 s    | 0.28 m         | 3.92 m    | at 164 s   | 3.92 m east  | 3.87 m       |
| v1_b   | no walls   | 167 s    | 0.28 m         | 0.51 m    | never      | 0.24 m east  | 0.44 m       |
| v1_c   | no walls   | 430 s    | 0.30 m         | 0.82 m    | never      | 0.53 m east  | 0.54 m       |
| v1b_a  | walls      | 343 s    | 0.10 m         | 0.11 m    | never      | 0.02 m       | 0.07 m       |
| v1b_c  | walls      | 402 s    | 0.11 m         | 0.17 m    | never      | 0.17 m east  | 0.06 m       |

Findings:
- Without walls, all three hovers leaned east (0.24-3.92 m) with little north-south motion,
  while SLAM reported ~0: the unconstrained direction. One exceeded 1 m (after 164 s).
- With walls, both hovers stayed within 0.17 m for 6-7 min; SLAM error under 0.07 m.
- First-minute wobble ~0.29 m without walls vs ~0.10 m with walls (~2.7x).
- Conclusion: the east-west drift is consistent with geometric degeneracy; adding
  east/west-facing surfaces removes it. Small sample (3 vs 2 runs); large drift is intermittent.
- v1_b was cut short (167 s) before the time at which v1_a drifted.

## Excluded run: hover_v1b_b2 (startup failure)
FAST-LIO2 reported z = -11.7 m while the drone sat on the ground. The preflight check only
tested PX4's validity flags, so it passed. On takeoff PX4 followed the bad estimate: the
drone climbed to 13.4 m, then settled at 6.0 m up and ~3-4.7 m north while SLAM reported
2.5 m up over the takeoff point. Not a degeneracy result; excluded.
Fixes: preflight now also requires the SLAM position on the ground within +/-0.3 m of zero;
the geofence gained a 5 m ceiling. Likely cause: FAST-LIO2 started before the simulator
settled (unconfirmed); procedure now waits a full minute after starting the simulator.
