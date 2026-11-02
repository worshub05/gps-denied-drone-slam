# Day 25: sensor noise robustness

Finding first: the IMU FAST-LIO2 uses (/iris/imu, gazebo_ros imu sensor) had NO noise in the
original model; all earlier results used a perfect IMU. Lidar noise was 0.01 m.
Variants (tools/set_drone_model.sh normal|realistic|heavy; model files iris_<variant>.sdf):
- realistic: IMU noise from Gazebo's IMU example (gyro 2e-4 rad/s, bias 7.5e-6; accel
  1.7e-2 m/s^2, bias 0.1), lidar 0.01 m
- heavy: 3x the realistic IMU noise and bias, lidar 0.03 m (3x)
Noise verified from recordings (drone on the ground, first 500 IMU samples): noise-free gyro
std 0.000000 rad/s; realistic 0.000205 rad/s and accel 0.0168 m/s^2 (targets 0.0002, 0.017).
All runs in outdoor_v1b (walls world) so noise effects are not mixed with east-west degeneracy.
Raw scores: results/day25_scores.txt.

## Hover (takeoff_hover)
| Model      | Airborne    | First 60 s max | Max drift   | SLAM err max |
|------------|-------------|----------------|-------------|--------------|
| noise-free | 343 / 402 s | 0.10 / 0.11 m  | 0.11 / 0.17 m | 0.07 / 0.06 m |
| realistic  | 502 s       | 0.07 m         | 0.17 m      | 0.05 m       |
| heavy      | 222 s       | 0.15 m         | 0.15 m      | 0.07 m       |

## behind_wall route (follow_path)
| Model      | Mean dev      | Max dev       | Min clearance | Landing vs goal |
|------------|---------------|---------------|---------------|-----------------|
| noise-free | 0.13-0.22 m   | 0.60-0.61 m   | 2.28-2.34 m   | 0.20-0.54 m     |
| realistic  | 0.10 m        | 0.35 m        | 2.24 m        | 0.28 m          |
| heavy      | 0.21 m        | 0.76 m        | 2.40 m        | 0.38 m          |

Conclusion: realistic IMU noise has no measurable effect; 3x IMU and 3x lidar noise raise the
worst-case route deviation slightly (0.76 m vs ~0.6 m). Far smaller than the effect of missing
east/west geometry (original world: mean 0.56 m, max 1.51 m). Single run per noise level.
