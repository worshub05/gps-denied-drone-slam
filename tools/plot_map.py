import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WS = os.path.expanduser('~/gpsdenied_ws')
meta = json.load(open(os.path.join(WS, 'maps', 'map_meta.json')))
occ = np.load(os.path.join(WS, 'maps', 'obstacle_map.npy'))
inf = np.load(os.path.join(WS, 'maps', 'obstacle_map_inflated.npy'))
h = meta['half']
ext = [-h, h, -h, h]
# known obstacles: world position minus takeoff point (~1, 1)
known = {'wall_north': (-1, 7),
         'tree_1': (2, -7), 'tree_2': (-9, 3), 'rock_1': (5, 1), 'rock_2': (-5, -6)}
img = np.zeros(occ.shape)
img[inf] = 0.35
img[occ] = 1.0
fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(img.T, origin='lower', extent=ext, cmap='Greys', vmin=0, vmax=1)
for name, (x, y) in known.items():
    ax.plot(x, y, 'r+', ms=12)
    ax.annotate(name, (x, y), color='red', fontsize=8, xytext=(4, 4), textcoords='offset points')
ax.plot(0, 0, 'bo', ms=6)
ax.annotate('takeoff', (0, 0), color='blue', fontsize=8, xytext=(4, -10), textcoords='offset points')
ax.set_xlabel('x east (m)')
ax.set_ylabel('y north (m)')
ax.set_title('Obstacle map: black = obstacle, grey = 2 m safety margin, red + = true position')
fig.tight_layout()
out = os.path.join(WS, 'results', 'plots', 'day15_obstacle_map.png')
fig.savefig(out, dpi=120)
print('saved', out, '| occupied cells:', int(occ.sum()), '| blocked incl. margin:', int(inf.sum()))
