# A* path planner on the inflated obstacle map (Day 15).
# Map frame: FAST-LIO2 world (origin at takeoff, x east, y north).
# PX4 frame used by the flight scripts: x east, y south, z down.
import argparse
import heapq
import json
import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WS = os.path.expanduser('~/gpsdenied_ws')
meta = json.load(open(os.path.join(WS, 'maps', 'map_meta.json')))
occ = np.load(os.path.join(WS, 'maps', 'obstacle_map.npy'))
inf = np.load(os.path.join(WS, 'maps', 'obstacle_map_inflated.npy'))
RES, HALF = meta['res'], meta['half']
N = inf.shape[0]
SQ2 = math.sqrt(2)
MOVES = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
         (1, 1, SQ2), (1, -1, SQ2), (-1, 1, SQ2), (-1, -1, SQ2)]


def to_cell(x, y):
    return int(math.floor((x + HALF) / RES)), int(math.floor((y + HALF) / RES))


def to_xy(c):
    return (c[0] + 0.5) * RES - HALF, (c[1] + 0.5) * RES - HALF


def inside(c):
    return 0 <= c[0] < N and 0 <= c[1] < N


from scipy.ndimage import distance_transform_edt
CLEAR = distance_transform_edt(~occ) * RES          # m to the nearest obstacle
SOFT = 3.5                                          # prefer staying this far away
W = 2.0                                             # extra cost at the 2 m margin edge
PEN = 1.0 + W * np.clip((SOFT - CLEAR) / (SOFT - meta['inflate_m']), 0.0, 1.0)


from scipy.ndimage import distance_transform_edt
CLEAR = distance_transform_edt(~occ) * RES          # m to the nearest obstacle
SOFT = 3.5                                          # prefer staying this far away
W = 2.0                                             # extra cost at the 2 m margin edge
PEN = 1.0 + W * np.clip((SOFT - CLEAR) / (SOFT - meta['inflate_m']), 0.0, 1.0)


def astar(start, goal):
    def h(c):
        dx, dy = abs(c[0] - goal[0]), abs(c[1] - goal[1])
        return dx + dy + (SQ2 - 2) * min(dx, dy)
    g = {start: 0.0}
    came = {}
    heap = [(h(start), start)]
    while heap:
        f, c = heapq.heappop(heap)
        if c == goal:
            path = [c]
            while c in came:
                c = came[c]
                path.append(c)
            return path[::-1]
        if f > g[c] + h(c) + 1e-9:
            continue
        for dx, dy, cost in MOVES:
            n = (c[0] + dx, c[1] + dy)
            if not inside(n) or inf[n]:
                continue
            ng = g[c] + cost * PEN[n]
            if ng < g.get(n, float('inf')):
                g[n] = ng
                came[n] = c
                heapq.heappush(heap, (ng + h(n), n))
    return None


def cells_on(a, b):
    steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
    return [(int(round(a[0] + k / steps * (b[0] - a[0]))),
             int(round(a[1] + k / steps * (b[1] - a[1])))) for k in range(steps + 1)]


def line_ok(a, b, min_clear):
    return all(not inf[c] and CLEAR[c] >= min_clear - 1e-6 for c in cells_on(a, b))


def simplify(path):
    out = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1:
            if line_ok(path[i], path[j], min(CLEAR[q] for q in path[i:j + 1])):
                break
            j -= 1
        out.append(path[j])
        i = j
    return out


ap = argparse.ArgumentParser()
ap.add_argument('--goal', nargs=2, type=float, required=True, help='goal x y in map frame (m)')
ap.add_argument('--start', nargs=2, type=float, default=[0.0, 0.0])
ap.add_argument('--alt', type=float, default=3.0, help='flight height (m)')
ap.add_argument('--name', default='test')
a = ap.parse_args()

s, gl = to_cell(*a.start), to_cell(*a.goal)
for label, c, xy in (('start', s, a.start), ('goal', gl, a.goal)):
    if not inside(c):
        raise SystemExit(f'{label} {xy} is outside the map')
    if inf[c]:
        raise SystemExit(f'{label} {xy} is inside an obstacle or its 2 m safety margin, no plan')

path = astar(s, gl)
if path is None:
    raise SystemExit('no path found')
wps = simplify(path)
wp_xy = [tuple(a.start)] + [to_xy(c) for c in wps[1:-1]] + [tuple(a.goal)]
length = sum(math.dist(wp_xy[i], wp_xy[i + 1]) for i in range(len(wp_xy) - 1))
direct = math.dist(a.start, a.goal)
px4 = [(round(x, 2), round(-y, 2), -a.alt) for x, y in wp_xy]

cl = min(CLEAR[c] for k in range(len(wp_xy) - 1) for c in cells_on(to_cell(*wp_xy[k]), to_cell(*wp_xy[k + 1])))
print(f'path found: {len(wp_xy)} waypoints, {length:.1f} m (straight line {direct:.1f} m), minimum clearance {cl:.2f} m')
for i, ((x, y), p) in enumerate(zip(wp_xy, px4)):
    print(f'  {i}: map ({x:6.2f}, {y:6.2f})   PX4 {p}')

json.dump({'name': a.name, 'alt': a.alt, 'length_m': length,
           'waypoints_map': wp_xy, 'waypoints_px4': px4},
          open(os.path.join(WS, 'maps', f'path_{a.name}.json'), 'w'), indent=2)

img = np.zeros(occ.shape)
img[inf] = 0.35
img[occ] = 1.0
fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(img.T, origin='lower', extent=[-HALF, HALF, -HALF, HALF], cmap='Greys', vmin=0, vmax=1)
raw = np.array([to_xy(c) for c in path])
ax.plot(raw[:, 0], raw[:, 1], color='tab:orange', lw=1, label='A* cells')
w = np.array(wp_xy)
ax.plot(w[:, 0], w[:, 1], 'b-o', ms=4, lw=2, label='waypoints')
ax.plot(*a.start, 'go', ms=8, label='start')
ax.plot(*a.goal, 'r*', ms=14, label='goal')
ax.set_xlabel('x east (m)')
ax.set_ylabel('y north (m)')
ax.set_title(f'Path "{a.name}": {length:.1f} m, {len(wp_xy)} waypoints')
ax.legend(loc='lower left', fontsize=8)
fig.tight_layout()
out = os.path.join(WS, 'results', 'plots', f'day16_path_{a.name}.png')
fig.savefig(out, dpi=120)
print('saved', out)
