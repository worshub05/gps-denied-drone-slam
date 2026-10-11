import math, random, zlib, struct, os

ROOT = os.path.expanduser('~/gpsdenied_ws/src/drone_control')
MODELS = os.path.join(ROOT, 'models', 'terrain_v2')
WORLD = os.path.join(ROOT, 'worlds', 'outdoor_v2.world')
os.makedirs(MODELS, exist_ok=True)
random.seed(7)

SIZE = 200.0   # terrain width and length (m)
HMAX = 15.0    # maximum terrain height (m)
N = 513        # heightmap pixels per side (2^9 + 1)
BUILD = (-25.0, -20.0)

HILLS = [(random.uniform(-90, 90), random.uniform(-90, 90),
          random.uniform(3, 9), random.uniform(12, 28)) for _ in range(14)]

def dist_to_square(x, y):
    dx = max(0 - x, 0, x - 5)
    dy = max(0 - y, 0, y - 5)
    return math.hypot(dx, dy)

def height(x, y):
    s = sum(A * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * sg * sg))
            for hx, hy, A, sg in HILLS)
    flat = min(1.0, max(0.0, (dist_to_square(x, y) - 4.0) / 12.0))
    return min(HMAX - 1.0, max(0.0, s * flat))

def png_gray(path, w, h, rows):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

rows = []
for r in range(N):
    y = -SIZE / 2 + r * SIZE / (N - 1)
    rows.append([min(255, int(round(height(-SIZE / 2 + c * SIZE / (N - 1), y) / HMAX * 255)))
                 for c in range(N)])
png_gray(os.path.join(MODELS, 'heightmap.png'), N, N, rows)

def free(x, y, clear=3.0):
    return (dist_to_square(x, y) > clear and math.hypot(x, y) > 6 and
            math.hypot(x - BUILD[0], y - BUILD[1]) > 14 and abs(x) < 95 and abs(y) < 95)

def link_part(name, pose, geom, material):
    return (f'        <collision name="{name}_c"><pose>{pose}</pose><geometry>{geom}</geometry></collision>\n'
            f'        <visual name="{name}_v"><pose>{pose}</pose><geometry>{geom}</geometry>'
            f'<material><script><uri>file://media/materials/scripts/gazebo.material</uri>'
            f'<name>{material}</name></script></material></visual>')

def model_xml(name, x, y, z, yaw, parts):
    return (f'    <model name="{name}">\n      <static>true</static>\n'
            f'      <pose>{x:.2f} {y:.2f} {z:.2f} 0 0 {yaw:.3f}</pose>\n'
            f'      <link name="link">\n' + '\n'.join(parts) + '\n      </link>\n    </model>')

def tree_model(i, x, y):
    r = random.uniform(1.4, 2.2)
    parts = [
        link_part('trunk', '0 0 1.5 0 0 0',
                  '<cylinder><radius>0.22</radius><length>3.0</length></cylinder>', 'Gazebo/Wood'),
        link_part('canopy', '0 0 4.5 0 0 0',
                  f'<sphere><radius>{r:.2f}</radius></sphere>', 'Gazebo/Green'),
    ]
    return model_xml(f'tree_{i}', x, y, height(x, y), random.uniform(0, 6.28), parts)

def rock_model(i, x, y):
    sx, sy, sz = random.uniform(0.6, 2.2), random.uniform(0.6, 2.2), random.uniform(0.5, 1.6)
    z = height(x, y) + sz / 2 - 0.2
    parts = [link_part('rock', '0 0 0 0 0 0',
                       f'<box><size>{sx:.2f} {sy:.2f} {sz:.2f}</size></box>',
                       random.choice(['Gazebo/Grey', 'Gazebo/DarkGrey']))]
    return model_xml(f'rock_{i}', x, y, z, random.uniform(0, 6.28), parts)

# Trees: 4 clustered patches plus scattered single trees
tree_spots = []
for _ in range(4):
    cx, cy = random.uniform(-70, 70), random.uniform(-70, 70)
    for _ in range(22):
        x, y = random.gauss(cx, 9), random.gauss(cy, 9)
        if free(x, y):
            tree_spots.append((x, y))
for _ in range(30):
    x, y = random.uniform(-90, 90), random.uniform(-90, 90)
    if free(x, y):
        tree_spots.append((x, y))
trees = [tree_model(i, x, y) for i, (x, y) in enumerate(tree_spots)]

# Rocks: scattered boulders plus 2 rock fields
rock_spots = []
for _ in range(2):
    cx, cy = random.uniform(-60, 60), random.uniform(-60, 60)
    for _ in range(6):
        x, y = random.gauss(cx, 3), random.gauss(cy, 3)
        if free(x, y, 2.5):
            rock_spots.append((x, y))
for _ in range(35):
    x, y = random.uniform(-90, 90), random.uniform(-90, 90)
    if free(x, y, 2.5):
        rock_spots.append((x, y))
rocks = [rock_model(i, x, y) for i, (x, y) in enumerate(rock_spots)]

# Farmhouse with roof and door
bz = height(*BUILD)
house = [model_xml('house', BUILD[0], BUILD[1], bz, 0.3, [
    link_part('body', '0 0 2.5 0 0 0', '<box><size>12 9 5</size></box>', 'Gazebo/Grey'),
    link_part('roof', '0 0 5.25 0 0 0', '<box><size>12.6 9.6 0.5</size></box>', 'Gazebo/Red'),
    link_part('door', '0 -4.55 1.1 0 0 0', '<box><size>1.2 0.1 2.2</size></box>', 'Gazebo/DarkGrey'),
])]

# Wooden fence along y = -40 with posts and rails
fence = []
for k, x in enumerate(range(-40, 41, 4)):
    fence.append(model_xml(f'post_{k}', x, -40, height(x, -40), 0, [
        link_part('post', '0 0 0.7 0 0 0', '<box><size>0.12 0.12 1.4</size></box>', 'Gazebo/Wood')]))
    if x < 40:
        xm = x + 2
        fence.append(model_xml(f'rail_{k}', xm, -40, height(xm, -40), 0, [
            link_part('rail', '0 0 1.1 0 0 0', '<box><size>4.0 0.06 0.06</size></box>', 'Gazebo/Wood')]))

header = '''<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="outdoor_v2">
    <include><uri>model://sun</uri></include>
    <physics name="default_physics" default="0" type="ode">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
    </physics>
    <scene>
      <ambient>0.45 0.45 0.45 1</ambient>
      <background>0.62 0.78 0.92 1</background>
      <shadows>1</shadows>
    </scene>
    <model name="terrain">
      <static>true</static>
      <link name="link">
        <collision name="col">
          <geometry><heightmap><uri>model://terrain_v2/heightmap.png</uri><size>200 200 15</size><pos>0 0 0</pos></heightmap></geometry>
        </collision>
        <visual name="vis">
          <geometry><heightmap>
            <uri>model://terrain_v2/heightmap.png</uri><size>200 200 15</size><pos>0 0 0</pos>
            <texture><diffuse>file://media/materials/textures/dirt_diffusespecular.png</diffuse><normal>file://media/materials/textures/flat_normal.png</normal><size>20</size></texture>
            <texture><diffuse>file://media/materials/textures/grass_diffusespecular.png</diffuse><normal>file://media/materials/textures/flat_normal.png</normal><size>20</size></texture>
            <blend><min_height>2</min_height><fade_dist>3</fade_dist></blend>
          </heightmap></geometry>
        </visual>
      </link>
    </model>
'''
footer = '  </world>\n</sdf>\n'

with open(WORLD, 'w') as f:
    f.write(header + '\n'.join(trees + rocks + house + fence) + '\n' + footer)

print(f'trees: {len(trees)}  rocks: {len(rocks)}  fence parts: {len(fence)}')
print(f'heightmap: {os.path.join(MODELS, "heightmap.png")}')
print(f'world: {WORLD}')
