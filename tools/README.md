# tools/

| Script | Purpose |
|--------|---------|
| `lidar_ring_time_relay.py` | Adds per-point `ring` and `time` fields to Gazebo's lidar cloud for FAST-LIO2 |
| `fastlio_to_px4.py` | Bridge: FAST-LIO2 `/Odometry` to PX4 `/fmu/in/vehicle_visual_odometry` (FLU to FRD) |
| `px4_params.sh` | Switch PX4 between GPS-denied (`slam`) and GPS (`gps`) settings |
| `obstacle_mapper.py` | 2D obstacle grid from FAST-LIO2's `/cloud_registered`, with 2 m inflation |
| `astar_planner.py` | A* route planner with clearance preference; writes `maps/path_<name>.json` |
| `follow_path.py` | Flies a planned route in offboard mode (corner hold), then lands |
| `square_flight_slam.py`, `lawnmower_flight_slam.py` | Fixed test flights in the GPS-denied frame |
| `lawnmower_flight.py` | Lawnmower survey in the GPS (north-east) frame |
| `gt_geofence.py` | Simulator-only safety net: stops the flight script if ground truth leaves the safe area |
| `odom_to_tum.py`, `bag_to_tum.py` | Convert recordings to TUM trajectories for evo |
| `drift_per_distance.py` | Position error over fixed-length path segments |
| `compare_frames.py` | Checks the bridge's axis conversion against PX4's estimate |
| `summarize_runs.py` | Week 2 summary table and trajectory plots (airborne-only) |
| `eval_path_follow.py` | Deviation from the planned route and real clearance from obstacles |
| `plot_map.py`, `demo_viz.py` | Map plot; RViz replay of a flight (with `docs/demo.rviz`) |
| `make_world_v2.py` | Generator for the larger outdoor_v2 world (not used for results) |
| `add_lidar.py`, `swap_to_3d_lidar.py` | One-off model edits that added the lidars |
| `stop_all.sh` | Stops the simulator and every node and script above |
