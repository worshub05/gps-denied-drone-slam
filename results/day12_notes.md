# Day 12: FAST-LIO2 to PX4 bridge (part 1)

PX4 version: v1.14.3.
Bridge: tools/fastlio_to_px4.py converts /Odometry (FAST-LIO2, x fwd / y left / z up)
to /fmu/in/vehicle_visual_odometry (FRD: flip y and z for position; q -> (w, x, -y, -z)).

Findings:
- PX4 v1.14.3 default EKF2_EV_CTRL = 15, so PX4 fuses vision data as soon as the bridge
  publishes, mixing it with GPS (EKF2_GPS_CTRL = 7). Set EKF2_EV_CTRL = 0 (saved) for the
  bridge-only comparison. Days 6-11 did not run the bridge, so their results are unaffected.
- `pkill -f "ros2 run"` stopped the launcher but not the flight script, leaving an old
  square_flight sending the start setpoint. Two controllers made the drone hover 0.9 m
  short of a corner. Fixed with tools/stop_all.sh, which stops the scripts directly.

Next: confirm the bridge axes against PX4 and ground truth at a square corner, then switch
PX4 to vision (EKF2_EV_CTRL 11, EKF2_GPS_CTRL 0, EKF2_HGT_REF 3, EKF2_EV_DELAY 50).

## Part 2: PX4 switched to vision (GPS off)
Settings (saved): EKF2_EV_CTRL 11, EKF2_GPS_CTRL 0, EKF2_HGT_REF 3, EKF2_EV_DELAY 50, EKF2_MAG_TYPE 5.
To fly on GPS again: EKF2_EV_CTRL 0, EKF2_GPS_CTRL 7, EKF2_HGT_REF 1, EKF2_MAG_TYPE 0.
Bridge axes verified with tools/compare_frames.py: matches PX4 with a fixed 90 deg heading
offset (FRD x = drone's initial heading = east) and ~0.1 m height offset.

## Part 3: hover on SLAM alone
Hover 1, outdoor_v1: height and north-south held, but east-west drifted 1.75 m in ~30 s
(truth x 1.08 -> 2.83) while FAST-LIO2 reported x ~0 (bouncing +/-0.4 m).
Cause: degeneracy. Flat ground fixes height, the north wall fixes north-south, rocks are
below the lidar's lowest beam at 2.6 m, and two thin distant tree trunks barely constrain
east-west. Hidden in Days 9-11 because GPS was flying the drone; with SLAM in the control
loop, the weak x estimate turns into real movement.
Fix: outdoor_v1b.world = outdoor_v1 + two 3 m walls facing east-west at x = -7 and x = 12.
Hover 2, outdoor_v1b: stable. Truth x 1.00-1.43 m (returned to 1.01), y 1.02-1.08 m,
z 2.62-2.67 m over 25 s. PX4 estimate held within ~0.1 m of the setpoint.
Landing: auto-land after offboard stopped, truth z 0.10 m, disarmed. FAST-LIO2 after landing
(-0.04, -0.09, 0.05), within 0.1 m of the takeoff point and steady.
