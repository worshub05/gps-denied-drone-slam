# Day 15: obstacle map from FAST-LIO2

Method: tools/obstacle_mapper.py accumulates /cloud_registered (FAST-LIO2 world frame:
origin at takeoff, x east, y north, z up) into a 2D grid. Resolution 0.2 m, extent +/-20 m,
height band 0.5-4.0 m, a cell counts as an obstacle after 3 hits, and points within 1 m of
the drone are ignored (rotor self-hits). Inflated copy grows obstacles by 2 m (Day 13 margin).
Built offline by replaying slam_lawn_02 (lidar + IMU) through FAST-LIO2. World: outdoor_v1.

## Result: 385 obstacle cells, 4038 cells blocked with margin, no false blobs
| Object     | Expected (map) | Found                    | Cells |
|------------|----------------|--------------------------|-------|
| north wall | (-1, 7)        | (-0.9, 6.8), x -6.6..4.2 | 176   |
| rock_2     | (-5, -6)       | (-5.1, -6.1)             | 94    |
| rock_1     | (5, 1)         | (4.8, 0.8)               | 64    |
| tree_2     | (-9, 3)        | (-9.0, 2.9)              | 27    |
| tree_1     | (2, -7)        | (1.8, -7.1)              | 24    |
All six objects found within ~0.2 m. Map frame = world minus takeoff point (~1, 1).

## Finding: rotor self-hits
Without the 1 m self-filter, the lidar's returns from the drone's own rotors (just beyond
FAST-LIO2's 0.3 m cutoff) filled the whole flight area with a false 1731-cell obstacle.
Note: a mapper started before the replay ends saves a partial map; wait for the full replay.
