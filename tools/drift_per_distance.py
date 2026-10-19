import sys
import numpy as np
from evo.tools import file_interface
from evo.core import sync

ref = file_interface.read_tum_trajectory_file(sys.argv[1])
est = file_interface.read_tum_trajectory_file(sys.argv[2])
seg = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
ref, est = sync.associate_trajectories(ref, est, max_diff=0.1)
est.align(ref)
P, Q = ref.positions_xyz, est.positions_xyz
dist = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
errs = []
for i in range(len(P)):
    j = np.searchsorted(dist, dist[i] + seg)
    if j >= len(P):
        break
    errs.append(np.linalg.norm((Q[j] - Q[i]) - (P[j] - P[i])))
errs = np.array(errs)
print(f"segments: {len(errs)}, segment length: {seg} m, total path: {dist[-1]:.1f} m")
print(f"mean {errs.mean():.3f} m ({100 * errs.mean() / seg:.2f}%), "
      f"median {np.median(errs):.3f} m, max {errs.max():.3f} m")
