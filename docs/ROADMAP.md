# Roadmap after v1.0

Each phase ends in a working, documented release. Day counts are estimates.
New experiments use new world files; v1.0 results stay tied to outdoor_v1.
After editing a launch file, rebuild drone_control so the install/ copy updates.

| Day   | Task | Release |
|-------|------|---------|
| 22    | Record the RViz replay demo (pending from Day 19); add a GIF to the README | v1.0 docs |
| **Phase A: stronger results** | | |
| 23    | Walls test: launch outdoor_v1b correctly; repeat the SLAM-only hover in both worlds to confirm or rule out the east-west degeneracy | |
| 24    | Repeat runs: behind_wall x3, SLAM-only lawnmower x2; report mean and spread | |
| 25    | Sensor noise: ~3x lidar and IMU noise; rerun square and behind_wall | |
| 26    | Wind: PX4 Gazebo wind plugin (steady + gusts); hover and behind_wall | |
| 27    | Update results and README | v1.1 |
| **Phase B: voice control** | | |
| 28    | Microphone access (WSL or Windows); Vosk offline speech recognition with a fixed command grammar | |
| 29    | Command node with typed commands: take off, hover, land, go home, go to named places, move N metres (via planner + follower) | |
| 30    | Voice input + safety: confidence threshold, "land"/"stop" always take priority, confirmation for long routes | |
| 31    | Voice demo video and docs | v1.2 |
| **Phase C: harder environments** | | |
| 32    | Denser structured world (outdoor_v3: corridors / warehouse-like); map, plan, fly | |
| 33    | Lighter outdoor_v2 (fewer trees and rocks) to make the procedural terrain usable | |
| 34    | Live mapping during flight and replanning when new obstacles appear | v1.3 |
| **Phase D: moving obstacles** | | |
| 35-36 | Moving obstacle in Gazebo; short-term map layer that clears freed space | |
| 37    | Replanning loop (~1 Hz) with safety stop | |
| 38    | Dynamic avoidance demo, docs, release | v2.0 |
