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
