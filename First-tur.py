
#   Dragon Animation  
#   Built with Python's-tkinter 


import tkinter as tk
import math
import random
import time



#  Window and Canvas Setup


WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 740

window = tk.Tk()
window.title("Dragon  —  move your mouse")
window.resizable(False, False)
window.configure(bg='#000000')

canvas = tk.Canvas(
    window,
    width  = WINDOW_WIDTH,
    height = WINDOW_HEIGHT,
    bg     = '#020209',
    highlightthickness = 0
)
canvas.pack()



#  Colours  (dark navy/blue palette — restrained and moody)


COLOR_BODY_DARK     = '#0a2840'   # main body fill
COLOR_BODY_EDGE     = '#1868a8'   # body outline
COLOR_BELLY         = '#18507a'   # lighter belly strip
COLOR_SHINE         = '#205878'   # dorsal highlight
COLOR_SCALE_DOT     = '#1060a0'   # little scale dots
COLOR_SPIKE_FILL    = '#1878b8'   # spine spike fill
COLOR_SPIKE_EDGE    = '#50c0ff'   # spine spike glow edge
COLOR_TAIL_FILL     = '#2090d0'
COLOR_TAIL_EDGE     = '#60d0ff'
COLOR_WING_FILL     = '#050d1a'   # dark semi-transparent wing membrane
COLOR_WING_EDGE     = '#0e2840'
COLOR_WING_BONE     = '#1a4870'   # finger bones
COLOR_WING_VEIN     = '#102840'   # membrane veins
COLOR_HEAD_FILL     = '#0a2840'
COLOR_HEAD_EDGE     = '#2888c8'
COLOR_SNOUT_FILL    = '#0c3050'
COLOR_JAW_FILL      = '#0c2840'
COLOR_JAW_EDGE      = '#205878'
COLOR_HORN_FILL     = '#0e3a60'
COLOR_HORN_EDGE     = '#40c0ff'
COLOR_NOSTRIL       = '#001828'
COLOR_EYE_GLOW      = '#004858'   
COLOR_EYE_IRIS      = '#00e8ff'   
COLOR_EYE_IRIS_EDGE = '#a0ffff'
COLOR_EYE_PUPIL     = '#000c14'
COLOR_HALO_OUTER    = '#001228'   
COLOR_HALO_MID      = '#001e38'
COLOR_GLOW_FAR      = '#000e1c'   
COLOR_GLOW_MID      = '#001628'
COLOR_GLOW_NEAR     = '#001e34'

# Particle colour palettes
FIRE_COLORS  = ['#ffffff', '#fff0c0', '#ffdd80', '#ffaa20', '#ff7700', '#ff4400', '#cc1100']
TRAIL_COLORS = ['#00ffff', '#40d8ff', '#80b8ff', '#c0e8ff', '#ffffff']
SPARK_COLORS = ['#ffffff', '#e0f8ff', '#a0e0ff']


#  Utility Functions


def flatten_points(point_list):
    """Convert a list of (x, y) tuples into a flat list [x0,y0,x1,y1,...]
    which is the format tkinter canvas expects for polygons."""
    return [coord for point in point_list for coord in point]


def move_oval(canvas_tag, center_x, center_y, radius_x, radius_y,
              fill='', outline='', width=1):
    """Reposition and recolour an oval canvas item in one call.
    Much easier than spelling out bounding-box coordinates every time."""
    canvas.coords(canvas_tag,
                  center_x - radius_x, center_y - radius_y,
                  center_x + radius_x, center_y + radius_y)
    canvas.itemconfig(canvas_tag, fill=fill, outline=outline, width=width)


def build_ribbon(spine_points, half_widths):
    """Given a list of spine (centreline) points and a matching list of
    half-widths, return two edge-point lists (left side, right side).

    The idea: at each spine point we find the direction of travel, rotate 90°
    to get the perpendicular, then offset left and right by the desired width.
    Joining left+right gives us a smooth filled body shape.
    """
    left_edge  = []
    right_edge = []
    total      = len(spine_points)

    for i in range(total):
        # Direction 
        if i == 0:
            # look forward
            dir_x = spine_points[1][0] - spine_points[0][0]
            dir_y = spine_points[1][1] - spine_points[0][1]
        elif i == total - 1:
            # look backward
            dir_x = spine_points[-1][0] - spine_points[-2][0]
            dir_y = spine_points[-1][1] - spine_points[-2][1]
        else:
            # smooth direction using neighbours
            dir_x = spine_points[i + 1][0] - spine_points[i - 1][0]
            dir_y = spine_points[i + 1][1] - spine_points[i - 1][1]

        length = math.hypot(dir_x, dir_y) or 1  # avoid division by zero
        #  (rotated 90° left)
        perp_x = -dir_y / length
        perp_y =  dir_x / length

        w = half_widths[i]
        cx, cy = spine_points[i]

        left_edge.append( (cx + perp_x * w, cy + perp_y * w) )
        right_edge.append((cx - perp_x * w, cy - perp_y * w) )

    return left_edge, right_edge



#  Background: Stars & Nebula


# Each star stores: (canvas_tag, x, y, radius, brightness, twinkle_speed, phase_offset)
stars = []
for _ in range(220):
    star_x      = random.uniform(0, WINDOW_WIDTH)
    star_y      = random.uniform(0, WINDOW_HEIGHT)
    star_radius = random.uniform(0.5, 2.2)
    brightness  = random.uniform(0.35, 1.0)   # max brightness of this star
    twinkle_speed = random.uniform(0.4, 2.8)  # how fast it pulses
    phase_offset  = random.uniform(0, 6.28)   # so they don't all pulse together

    tag = canvas.create_oval(
        star_x - star_radius, star_y - star_radius,
        star_x + star_radius, star_y + star_radius,
        fill='white', outline=''
    )
    stars.append((tag, star_x, star_y, star_radius, brightness, twinkle_speed, phase_offset))


# Nebula blobs — soft dark ovals layered behind everything to add depth
nebula_dark_colors = ['#050a18', '#040d14', '#060a10', '#08080e', '#04080f']
for _ in range(7):
    blob_x      = random.uniform(80, WINDOW_WIDTH  - 80)
    blob_y      = random.uniform(80, WINDOW_HEIGHT - 80)
    blob_width  = random.uniform(90, 200)
    blob_height = random.uniform(60, 140)
    color       = random.choice(nebula_dark_colors)
    canvas.create_oval(
        blob_x - blob_width,  blob_y - blob_height,
        blob_x + blob_width,  blob_y + blob_height,
        fill=color, outline=''
    )



#  Dragon Body Physics


NUM_SEGMENTS   = 34    # number of body joints (head is segment 0, tail is last)
SEGMENT_LENGTH = 15    # resting distance between each joint in pixels

# Start the dragon stretched out horizontally in the centre of the screen
body_joints = [[WINDOW_WIDTH // 2 + i * SEGMENT_LENGTH, WINDOW_HEIGHT // 2]
               for i in range(NUM_SEGMENTS)]

# Mouse target — the head will smoothly chase this point
mouse_x = WINDOW_WIDTH  // 2
mouse_y = WINDOW_HEIGHT // 2 - 120

def on_mouse_move(event):
    """Update the mouse target whenever the cursor moves."""
    global mouse_x, mouse_y
    mouse_x, mouse_y = event.x, event.y

canvas.bind('<Motion>', on_mouse_move)
window.bind('<Motion>', on_mouse_move)


def get_segment_half_width(segment_index):
    """Return how wide (in pixels, half-width) each body segment should be.
    The neck is thicker, the tail tapers to a thin point."""
    fraction = segment_index / (NUM_SEGMENTS - 1)  # 0.0 at head, 1.0 at tail tip

    if fraction < 0.06:
        # Very start of neck — moderate width
        return 11
    elif fraction < 0.18:
        # Shoulder — widest part
        return 15
    elif fraction < 0.50:
        # Main body tapering gradually
        return 15 - (fraction - 0.18) / 0.32 * 5.5
    else:
        # Tail — tapering to a thin tip
        return 9.5 - (fraction - 0.50) / 0.50 * 8.5



#  Canvas Item Creation  (order matters — drawn back-to-front)


# --- Soft glow ribbons that follow the body (drawn first, behind everything) ---
body_glow_far   = canvas.create_polygon([0] * 6, fill=COLOR_GLOW_FAR,  outline='', smooth=True)
body_glow_mid   = canvas.create_polygon([0] * 6, fill=COLOR_GLOW_MID,  outline='', smooth=True)
body_glow_near  = canvas.create_polygon([0] * 6, fill=COLOR_GLOW_NEAR, outline='', smooth=True)

# --- Wings (behind the body so the body overlaps them at the shoulder) ---
left_wing_membrane  = canvas.create_polygon([0] * 18, fill=COLOR_WING_FILL, outline=COLOR_WING_EDGE, width=1)
right_wing_membrane = canvas.create_polygon([0] * 18, fill=COLOR_WING_FILL, outline=COLOR_WING_EDGE, width=1)

left_wing_bones  = [canvas.create_line(0, 0, 0, 0, fill=COLOR_WING_BONE, width=2) for _ in range(4)]
right_wing_bones = [canvas.create_line(0, 0, 0, 0, fill=COLOR_WING_BONE, width=2) for _ in range(4)]

left_wing_veins  = [canvas.create_line(0, 0, 0, 0, fill=COLOR_WING_VEIN, width=1) for _ in range(4)]
right_wing_veins = [canvas.create_line(0, 0, 0, 0, fill=COLOR_WING_VEIN, width=1) for _ in range(4)]

# --- Main body ribbon (three layers: dark base, belly, dorsal shine) ---
body_main  = canvas.create_polygon([0] * 6, fill=COLOR_BODY_DARK, outline=COLOR_BODY_EDGE, width=1, smooth=True)
body_belly = canvas.create_polygon([0] * 6, fill=COLOR_BELLY,     outline='',              smooth=True)
body_shine = canvas.create_polygon([0] * 6, fill=COLOR_SHINE,     outline='',              smooth=True)

# --- Spine spikes along the back ---
NUM_SPIKES = 13
spine_spikes = [canvas.create_polygon([0] * 6, fill=COLOR_SPIKE_FILL, outline=COLOR_SPIKE_EDGE, width=1)
                for _ in range(NUM_SPIKES)]
tail_tip_spike = canvas.create_polygon([0] * 6, fill=COLOR_TAIL_FILL, outline=COLOR_TAIL_EDGE, width=1)

# --- Scale dots decorating the sides of the body ---
scale_dots = [canvas.create_oval(0, 0, 3, 3, fill=COLOR_SCALE_DOT, outline='', state='hidden')
              for _ in range(60)]

# --- Head parts (drawn from outermost glow inward) ---
head_halo_outer = canvas.create_oval(0, 0, 1, 1, fill=COLOR_HALO_OUTER, outline='')
head_halo_inner = canvas.create_oval(0, 0, 1, 1, fill=COLOR_HALO_MID,   outline='')
head_skull      = canvas.create_oval(0, 0, 1, 1, fill=COLOR_HEAD_FILL,  outline=COLOR_HEAD_EDGE, width=2)
head_snout      = canvas.create_oval(0, 0, 1, 1, fill=COLOR_SNOUT_FILL, outline=COLOR_HEAD_EDGE, width=1)
head_jaw        = canvas.create_polygon([0] * 8, fill=COLOR_JAW_FILL,  outline=COLOR_JAW_EDGE, width=1)
left_horn       = canvas.create_polygon([0] * 6, fill=COLOR_HORN_FILL, outline=COLOR_HORN_EDGE, width=1)
right_horn      = canvas.create_polygon([0] * 6, fill=COLOR_HORN_FILL, outline=COLOR_HORN_EDGE, width=1)
left_nostril    = canvas.create_oval(0, 0, 1, 1, fill=COLOR_NOSTRIL, outline='')
right_nostril   = canvas.create_oval(0, 0, 1, 1, fill=COLOR_NOSTRIL, outline='')

# --- Eyes (glow halo → iris → pupil, per eye) ---
left_eye_glow   = canvas.create_oval(0, 0, 1, 1, fill=COLOR_EYE_GLOW,  outline='')
right_eye_glow  = canvas.create_oval(0, 0, 1, 1, fill=COLOR_EYE_GLOW,  outline='')
left_eye_iris   = canvas.create_oval(0, 0, 1, 1, fill=COLOR_EYE_IRIS,  outline=COLOR_EYE_IRIS_EDGE, width=1)
right_eye_iris  = canvas.create_oval(0, 0, 1, 1, fill=COLOR_EYE_IRIS,  outline=COLOR_EYE_IRIS_EDGE, width=1)
left_eye_pupil  = canvas.create_oval(0, 0, 1, 1, fill=COLOR_EYE_PUPIL, outline='')
right_eye_pupil = canvas.create_oval(0, 0, 1, 1, fill=COLOR_EYE_PUPIL, outline='')



#  Particle System  (fire breath, tail trail, eye sparks, wing tips)


MAX_PARTICLES = 200

class Particle:
    """A single glowing dot that spawns, moves under simple physics, and fades out.
    We reuse instances from a pool instead of creating/destroying them every frame."""

    def __init__(self):
        # Create the canvas oval now (hidden until needed)
        self.canvas_tag = canvas.create_oval(-5, -5, -4, -4,
                                             fill='white', outline='', state='hidden')
        self.alive = False

    def spawn(self, x, y, vel_x, vel_y, color, size, lifespan):
        """Activate this particle at position (x, y) with the given properties."""
        self.x     = x + random.uniform(-3, 3)   # tiny random offset so clusters look natural
        self.y     = y + random.uniform(-3, 3)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.size  = size
        self.life     = lifespan
        self.max_life = lifespan
        self.alive    = True
        canvas.itemconfig(self.canvas_tag, state='normal')

    def update(self):
        """Move, age, and redraw the particle. Hide it when its life runs out."""
        if not self.alive:
            return

        # Simple physics: move, add gravity, add drag
        self.x     += self.vel_x
        self.y     += self.vel_y
        self.vel_y += 0.05    # gravity pulls downward
        self.vel_x *= 0.95    # horizontal drag

        self.life -= 1

        if self.life <= 0:
            self.alive = False
            canvas.itemconfig(self.canvas_tag, state='hidden')
            return

        # Shrink as life runs out
        age_fraction = self.life / self.max_life
        current_size = max(0.8, self.size * age_fraction)

        canvas.coords(self.canvas_tag,
                      self.x - current_size, self.y - current_size,
                      self.x + current_size, self.y + current_size)
        canvas.itemconfig(self.canvas_tag, fill=self.color)


# Create the particle pool (all hidden at start)
particle_pool = [Particle() for _ in range(MAX_PARTICLES)]

def get_free_particle():
    """Find the first inactive particle in the pool, or return None if all are busy."""
    for particle in particle_pool:
        if not particle.alive:
            return particle
    return None



#  Main Animation Loop

frame_count = 0
start_time  = time.time()

def animate():
    global frame_count
    frame_count += 1
    elapsed = time.time() - start_time   # seconds since start
    frame   = frame_count

    #  Twinkle the stars 
    for tag, sx, sy, sr, brightness, twinkle_speed, phase in stars:
        # Sine wave gives a smooth pulsing brightness
        glow   = 0.5 + 0.5 * math.sin(elapsed * twinkle_speed + phase)
        value  = int(max(0, min(255, (0.4 + 0.6 * glow) * brightness * 255)))
        blue   = min(255, value + 25)   # stars are slightly blue-tinted
        canvas.itemconfig(tag, fill=f'#{value:02x}{value:02x}{blue:02x}')

    #  Move the head toward the mouse (smooth follow) 
    head_x, head_y = body_joints[0]
    delta_x = mouse_x - head_x
    delta_y = mouse_y - head_y
    distance = math.hypot(delta_x, delta_y)

    if distance > 2:
        # Move a fraction of the remaining distance each frame (eased follow)
        step = min(distance * 0.14, 13)
        body_joints[0][0] += (delta_x / distance) * step
        body_joints[0][1] += (delta_y / distance) * step

    #  Pull body segments behind the head 
    # Each segment tries to stay exactly SEGMENT_LENGTH pixels behind its parent.
    for i in range(1, NUM_SEGMENTS):
        parent_x, parent_y = body_joints[i - 1]
        child_x,  child_y  = body_joints[i]

        offset_x = child_x - parent_x
        offset_y = child_y - parent_y
        dist     = math.hypot(offset_x, offset_y)

        if dist > SEGMENT_LENGTH:
            # Too far — pull the child closer
            ratio = SEGMENT_LENGTH / dist
            body_joints[i][0] = parent_x + offset_x * ratio
            body_joints[i][1] = parent_y + offset_y * ratio

    #  Compute head angle & per-segment widths 
    head_x, head_y = body_joints[0]

    # Direction the head is facing (looking away from the neck)
    head_angle = math.atan2(
        body_joints[0][1] - body_joints[1][1],
        body_joints[0][0] - body_joints[1][0]
    ) if NUM_SEGMENTS > 1 else 0.0

    # A slow sine pulse used for eye glow, halo breathing, etc.
    pulse = 0.5 + 0.5 * math.sin(elapsed * 2.8)

    # Half-widths for every segment
    segment_widths = [get_segment_half_width(i) for i in range(NUM_SEGMENTS)]

    # The body ribbon uses segments 1–end (head is drawn separately)
    body_spine  = body_joints[1:]
    body_widths = segment_widths[1:]

    #  Draw glow ribbons (three layers, each a little wider than the body) 
    for glow_tag, extra_width in [(body_glow_far, 14), (body_glow_mid, 9), (body_glow_near, 5)]:
        glow_widths = [w + extra_width for w in body_widths]
        left, right = build_ribbon(body_spine, glow_widths)
        glow_polygon = left + list(reversed(right))
        if len(glow_polygon) >= 3:
            canvas.coords(glow_tag, flatten_points(glow_polygon))

    #  Draw the main body ribbon (dark base + belly + shine) 
    left_edge, right_edge = build_ribbon(body_spine, body_widths)
    full_body_polygon     = left_edge + list(reversed(right_edge))
    if len(full_body_polygon) >= 3:
        canvas.coords(body_main, flatten_points(full_body_polygon))

    # Belly strip — narrower ribbon centred on the underside
    belly_widths       = [w * 0.42 for w in body_widths]
    belly_left, belly_right = build_ribbon(body_spine, belly_widths)
    belly_polygon      = belly_left + list(reversed(belly_right))
    if len(belly_polygon) >= 3:
        canvas.coords(body_belly, flatten_points(belly_polygon))

    # Dorsal shine — a thin highlight strip along the top
    shine_widths       = [w * 0.15 for w in body_widths]
    shine_left, shine_right = build_ribbon(body_spine, shine_widths)
    shine_polygon      = shine_left + list(reversed(shine_right))
    if len(shine_polygon) >= 3:
        canvas.coords(body_shine, flatten_points(shine_polygon))

    # Place scale dots along the body sides 
    dot_index = 0
    for seg in range(2, NUM_SEGMENTS - 2, 2):
        if dot_index + 1 >= len(scale_dots):
            break
        seg_x, seg_y    = body_joints[seg]
        side_reach      = segment_widths[seg] * 0.55
        perp_angle      = math.atan2(
            body_joints[seg][1] - body_joints[seg - 1][1],
            body_joints[seg][0] - body_joints[seg - 1][0]
        ) + math.pi / 2

        for side in [1, -1]:
            if dot_index >= len(scale_dots):
                break
            dot_x = seg_x + math.cos(perp_angle) * side_reach * side * 0.7
            dot_y = seg_y + math.sin(perp_angle) * side_reach * side * 0.7
            canvas.coords(scale_dots[dot_index], dot_x - 2, dot_y - 2, dot_x + 2, dot_y + 2)
            canvas.itemconfig(scale_dots[dot_index], state='normal')
            dot_index += 1

    # Draw the wings
    shoulder_x, shoulder_y = body_joints[5]
    flap_angle = math.sin(elapsed * 4.2)   # oscillates between -1 and +1

    for side_label, membrane, bones, veins in [
        ('right', right_wing_membrane, right_wing_bones, right_wing_veins),
        ('left',  left_wing_membrane,  left_wing_bones,  left_wing_veins),
    ]:
        direction   = 1 if side_label == 'right' else -1
        flap_offset = flap_angle * 0.38 * direction

        # Wing root — where the membrane attaches to the shoulder
        perp_to_body = head_angle + math.pi / 2
        root_x = shoulder_x + math.cos(perp_to_body) * 13 * direction
        root_y = shoulder_y + math.sin(perp_to_body) * 13 * direction

        # 4 finger-tips fan out from the root 
        finger_angles  = [0.50 + flap_offset, 0.78 + flap_offset,
                          1.10 + flap_offset, 1.40 + flap_offset]
        finger_lengths = [118, 88, 65, 44]

        finger_tips = []
        for angle_offset, length in zip(finger_angles, finger_lengths):
            finger_angle = head_angle + angle_offset * direction
            tip_x = root_x + math.cos(finger_angle) * length
            tip_y = root_y + math.sin(finger_angle) * length
            finger_tips.append((tip_x, tip_y))

        # Trailing edge anchor (behind the shoulder)
        trailing_angle = head_angle - 0.20 * direction
        trailing_x     = shoulder_x + math.cos(trailing_angle) * 32
        trailing_y     = shoulder_y + math.sin(trailing_angle) * 32

        # Membrane polygon: root → tips → trailing anchor
        membrane_coords = [root_x, root_y]
        for tip_x, tip_y in finger_tips:
            membrane_coords += [tip_x, tip_y]
        membrane_coords += [trailing_x, trailing_y]
        canvas.coords(membrane, *membrane_coords)

        # Finger bones and veins
        for i, (tip_x, tip_y) in enumerate(finger_tips):
            canvas.coords(bones[i], root_x, root_y, tip_x, tip_y)
            canvas.coords(veins[i], root_x, root_y, tip_x, tip_y)

    #  Draw spine spikes 
    for spike_num, spike_tag in enumerate(spine_spikes):
        seg_idx = 2 + spike_num * 2   # every other segment, starting from seg 2

        if seg_idx + 1 >= NUM_SEGMENTS:
            canvas.coords(spike_tag, 0, 0, 0, 0, 0, 0)
            continue

        seg_x, seg_y  = body_joints[seg_idx]
        next_x, next_y = body_joints[seg_idx + 1]

        # Spike points roughly perpendicular to the body direction (upward)
        spike_direction = math.atan2(seg_y - next_y, seg_x - next_x) + math.pi / 2

        # Spikes get shorter toward the tail; they also subtly animate
        spike_height  = (9.5 - spike_num * 0.45) + math.sin(elapsed * 3 + spike_num * 0.6) * 1.5
        spike_half_base = 2.5

        tip_x = seg_x + math.cos(spike_direction) * spike_height
        tip_y = seg_y + math.sin(spike_direction) * spike_height

        base_perp = spike_direction + math.pi / 2
        canvas.coords(spike_tag,
                      seg_x + math.cos(base_perp) * spike_half_base,
                      seg_y + math.sin(base_perp) * spike_half_base,
                      tip_x, tip_y,
                      seg_x - math.cos(base_perp) * spike_half_base,
                      seg_y - math.sin(base_perp) * spike_half_base)

    # Tail tip spike
    second_last_x, second_last_y = body_joints[-2]
    last_x,        last_y        = body_joints[-1]
    tail_direction = math.atan2(last_y - second_last_y, last_x - second_last_x)
    tail_perp      = tail_direction + math.pi / 2
    tail_tip_x     = last_x + math.cos(tail_direction) * 22
    tail_tip_y     = last_y + math.sin(tail_direction) * 22

    canvas.coords(tail_tip_spike,
                  last_x + math.cos(tail_perp) * 4, last_y + math.sin(tail_perp) * 4,
                  tail_tip_x, tail_tip_y,
                  last_x - math.cos(tail_perp) * 4, last_y - math.sin(tail_perp) * 4)

    #  Draw the head 
    halo_outer_radius = 24 + pulse * 7   # halo pulses gently
    halo_inner_radius = 17 + pulse * 4

    move_oval(head_halo_outer, head_x, head_y, halo_outer_radius, halo_outer_radius, COLOR_HALO_OUTER)
    move_oval(head_halo_inner, head_x, head_y, halo_inner_radius, halo_inner_radius, COLOR_HALO_MID)
    move_oval(head_skull,      head_x, head_y, 13, 12, COLOR_HEAD_FILL,  COLOR_HEAD_EDGE, 2)

    # Snout sits in front of the skull
    snout_x = head_x + math.cos(head_angle) * 14
    snout_y = head_y + math.sin(head_angle) * 14
    move_oval(head_snout, snout_x, snout_y, 6.5, 5.5, COLOR_SNOUT_FILL, COLOR_HEAD_EDGE, 1)

    # Jaw (lower mandible — a simple 4-point polygon)
    canvas.coords(head_jaw,
                  head_x  + math.cos(head_angle) * 4,              head_y  + math.sin(head_angle) * 4,
                  snout_x + math.cos(head_angle + math.pi/2) * 4,  snout_y + math.sin(head_angle + math.pi/2) * 4,
                  snout_x + math.cos(head_angle) * 7,              snout_y + math.sin(head_angle) * 7,
                  snout_x - math.cos(head_angle + math.pi/2) * 4,  snout_y - math.sin(head_angle + math.pi/2) * 4)

    # Nostrils (one on each side of the snout tip)
    side_axis = head_angle + math.pi / 2
    for side, nostril_tag in [(1, left_nostril), (-1, right_nostril)]:
        nx = snout_x + math.cos(side_axis) * 3.5 * side + math.cos(head_angle) * 2
        ny = snout_y + math.sin(side_axis) * 3.5 * side + math.sin(head_angle) * 2
        move_oval(nostril_tag, nx, ny, 1.5, 1.5, COLOR_NOSTRIL)

    # Horns (curved slightly backward for that classic dragon look)
    for side, horn_tag in [(1, left_horn), (-1, right_horn)]:
        horn_base_x = head_x + math.cos(side_axis) * 6 * side + math.cos(head_angle) * 3
        horn_base_y = head_y + math.sin(side_axis) * 6 * side + math.sin(head_angle) * 3
        horn_tip_x  = horn_base_x + math.cos(head_angle + 0.5 * side) * 19
        horn_tip_y  = horn_base_y + math.sin(head_angle + 0.5 * side) * 19
        horn_left   = (horn_base_x + math.cos(side_axis) * 2.5, horn_base_y + math.sin(side_axis) * 2.5)
        horn_right  = (horn_base_x - math.cos(side_axis) * 2.5, horn_base_y - math.sin(side_axis) * 2.5)
        canvas.coords(horn_tag, horn_left[0], horn_left[1], horn_tip_x, horn_tip_y,
                      horn_right[0], horn_right[1])

    # Eyes (positioned to the left and right of the head centreline)
    eye_radius = 3.5 + pulse * 0.8   # eyes pulse slightly with the heartbeat
    for side, glow_tag, iris_tag, pupil_tag in [
        ( 1, left_eye_glow,  left_eye_iris,  left_eye_pupil ),
        (-1, right_eye_glow, right_eye_iris, right_eye_pupil),
    ]:
        eye_x = head_x + math.cos(side_axis) * 5.5 * side + math.cos(head_angle) * 6
        eye_y = head_y + math.sin(side_axis) * 5.5 * side + math.sin(head_angle) * 6

        move_oval(glow_tag,  eye_x, eye_y, eye_radius + 3.5, eye_radius + 3.5, COLOR_EYE_GLOW)
        move_oval(iris_tag,  eye_x, eye_y, eye_radius,       eye_radius,       COLOR_EYE_IRIS, COLOR_EYE_IRIS_EDGE, 1)
        move_oval(pupil_tag,
                  eye_x + math.cos(head_angle) * 1.2,
                  eye_y + math.sin(head_angle) * 1.2,
                  1.8, 1.8, COLOR_EYE_PUPIL)

    # Spawn particles 

    # Fire breath from the mouth tip (every 2nd frame = ~30 puffs/sec)
    mouth_x = head_x + math.cos(head_angle) * 21
    mouth_y = head_y + math.sin(head_angle) * 21

    if frame % 2 == 0:
        for _ in range(6):
            p = get_free_particle()
            if p:
                fire_speed = random.uniform(3.5, 7.0)
                fire_angle = head_angle + random.uniform(-0.28, 0.28)   # slight spread
                p.spawn(
                    mouth_x, mouth_y,
                    math.cos(fire_angle) * fire_speed,
                    math.sin(fire_angle) * fire_speed,
                    random.choice(FIRE_COLORS[:5]),
                    random.uniform(4, 9),
                    random.randint(10, 26)
                )

    # Magical sparks drifting off each eye (every 5th frame)
    if frame % 5 == 0:
        for side in [1, -1]:
            p = get_free_particle()
            if p:
                eye_x = head_x + math.cos(side_axis) * 5.5 * side + math.cos(head_angle) * 6
                eye_y = head_y + math.sin(side_axis) * 5.5 * side + math.sin(head_angle) * 6
                drift_angle = random.uniform(0, math.pi * 2)
                p.spawn(
                    eye_x, eye_y,
                    math.cos(drift_angle) * 1.5,
                    math.sin(drift_angle) * 1.5,
                    random.choice(SPARK_COLORS),
                    random.uniform(1.5, 3.5),
                    random.randint(18, 35)
                )

    # Energy trail from the tail tip (every 2nd frame)
    if frame % 2 == 0:
        p = get_free_particle()
        if p:
            tail_tip_pos = body_joints[-1]
            drift_angle  = random.uniform(0, math.pi * 2)
            p.spawn(
                tail_tip_pos[0], tail_tip_pos[1],
                math.cos(drift_angle) * 0.8,
                math.sin(drift_angle) * 0.8,
                random.choice(TRAIL_COLORS),
                random.uniform(2, 5),
                random.randint(25, 55)
            )

    # Sparks off the wing tips (every 9th frame)
    if frame % 9 == 0:
        for wing_membrane in [left_wing_membrane, right_wing_membrane]:
            wing_coords = canvas.coords(wing_membrane)
            if len(wing_coords) >= 4:
                p = get_free_particle()
                if p:
                    p.spawn(
                        wing_coords[2], wing_coords[3],
                        random.uniform(-0.8, 0.8),
                        random.uniform(-0.8, 0.8),
                        random.choice(TRAIL_COLORS[:3]),
                        random.uniform(2, 4),
                        random.randint(15, 30)
                    )

    # Update all live particles 
    for particle in particle_pool:
        particle.update()

    # Schedule the next frame (60 FPS)
    window.after(16, animate)


# Kick off the animation and hand control to tkinter
animate()
window.mainloop()