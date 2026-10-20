import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from evo.tools import file_interface
from evo.core import sync

WS = os.path.expanduser('~/gpsdenied_ws')
BAGS = os.path.join(WS, 'bags')
PLOTS = os.path.join(WS, 'results', 'plots')
os.makedirs(PLOTS, exist_ok=True)

# (label, bag with /Odometry + ground truth, or None to use existing TUM prefix)
RUNS = [
    ('PX4 estimator, GPS on, square (Day 8)', None, 'run01'),
    ('FAST-LIO2 bag replay, square (Day 9, run 06)', 'fastlio_run_06', None),
    ('FAST-LIO2 live, square, GPS flying (Day 10)', 'fastlio_live_03', None),
    ('FAST-LIO2 live, lawnmower, GPS flying (Day 11)', 'fastlio_long_01', None),
    ('SLAM only, square (Day 13)', 'slam_square_01', None),
    ('SLAM only, lawnmower, default speed (Day 13)', 'slam_lawn_01', None),
    ('SLAM only, lawnmower, 2 m/s (Day 13)', 'slam_lawn_02', None),
]

rows = []
for label, bag, prefix in RUNS:
    try:
        if bag:
            prefix = 'sum_' + bag
            subprocess.run(['python3', os.path.join(WS, 'tools', 'odom_to_tum.py'), bag, prefix],
                           cwd=BAGS, check=True, capture_output=True)
        ref = file_interface.read_tum_trajectory_file(os.path.join(BAGS, prefix + '_gt.tum'))
        est = file_interface.read_tum_trajectory_file(os.path.join(BAGS, prefix + '_est.tum'))
        ref, est = sync.associate_trajectories(ref, est, max_diff=0.1)
        ids = np.where(ref.positions_xyz[:, 2] > 1.5)[0]
        ref.reduce_to_ids(ids)
        est.reduce_to_ids(ids)
        est.align(ref)
        P, Q = ref.positions_xyz, est.positions_xyz
        e = np.linalg.norm(P - Q, axis=1)
        path = float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1)))
        rows.append((label, path, float(np.sqrt(np.mean(e ** 2))), float(np.mean(e)),
                     float(np.median(e)), float(np.max(e)), len(e)))
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot(P[:, 0], P[:, 1], color='0.5', lw=2, label='ground truth')
        ax.plot(Q[:, 0], Q[:, 1], color='tab:blue', lw=1, label='estimate (aligned)')
        ax.set_aspect('equal')
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_title(f'{label}\nRMSE {rows[-1][2]:.3f} m, max {rows[-1][5]:.3f} m', fontsize=9)
        ax.legend(loc='best', fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, prefix + '.png'), dpi=120)
        plt.close(fig)
    except Exception as ex:
        print(f'SKIPPED {label}: {ex}')

lines = [
    '# Week 2 summary: trajectory accuracy (airborne only)',
    '',
    'Method: estimate vs Gazebo ground truth, samples with ground-truth height > 1.5 m only,',
    'SE(3) Umeyama alignment fitted on the airborne part, message header timestamps',
    '(Day 8 PX4 baseline uses its original recording-time conversion). Plots in results/plots/.',
    '',
    '| Run | Airborne path (m) | RMSE (m) | Mean (m) | Median (m) | Max (m) | Poses |',
    '|-----|-------------------|----------|----------|------------|---------|-------|',
]
for r in rows:
    lines.append(f'| {r[0]} | {r[1]:.1f} | {r[2]:.3f} | {r[3]:.3f} | {r[4]:.3f} | {r[5]:.3f} | {r[6]} |')
text = '\n'.join(lines) + '\n'
open(os.path.join(WS, 'results', 'week2_summary.md'), 'w').write(text)
print(text)
