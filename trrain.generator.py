import math
import random

# ==========================================
# GLOBAL SETTINGS
# ==========================================
START_X = 1.0  # Where all courses begin on the X-axis
LANE_WIDTH = 1.5 # Width of each course (Y-axis)

print('')
print('')
print('')

# ==========================================
# 1. VARIABLE RISER STAIRCASE (LANE 1)
# ==========================================
print('\n')
STAIRS_Y_OFFSET = -2.0

start_rise_cm = 1
end_rise_cm = 20
rise_increment_cm = 5
steps_per_group = 5
step_depth = 0.3

current_x = START_X
current_height_m = 0.0

for rise_cm in range(start_rise_cm, end_rise_cm + 1, rise_increment_cm):
    rise_m = rise_cm / 100.0
    print(f'    ')
    
    for i in range(steps_per_group):
        current_height_m += rise_m
        z_size = current_height_m / 2.0
        
        step_name = f"stair_rise{rise_cm}_{i+1}"
        print(f'    <geom name="{step_name}" type="box" '
              f'size="{step_depth/2:.3f} {LANE_WIDTH/2:.3f} {z_size:.4f}" '
              f'pos="{current_x:.3f} {STAIRS_Y_OFFSET} {z_size:.4f}" material="wood"/>')
        
        current_x += step_depth


# ==========================================
# 2. CONTINUOUS SLOPE / RAMP (LANE 2)
# ==========================================
print('\n')
RAMP_Y_OFFSET = 0.0

start_angle_deg = 5
end_angle_deg = 45
angle_increment_deg = 5
segment_length = 3.0
ramp_thickness = 0.1

current_x = START_X
current_z = 0.0

for angle_deg in range(start_angle_deg, end_angle_deg + 1, angle_increment_deg):
    theta_rad = math.radians(angle_deg)
    
    # Calculate dimensions for this segment
    dx = segment_length * math.cos(theta_rad)
    dz = segment_length * math.sin(theta_rad)
    
    # Box center position
    center_x = current_x + (dx / 2.0)
    center_z = current_z + (dz / 2.0)
    
    # Rotation in radians (Negative around Y-axis to pitch up)
    axis_angle_val = f"0 1 0 {-theta_rad:.4f}"
    
    print(f'    <geom name="ramp_{angle_deg}deg" type="box" '
          f'size="{segment_length/2:.3f} {LANE_WIDTH/2:.3f} {ramp_thickness/2:.3f}" '
          f'pos="{center_x:.4f} {RAMP_Y_OFFSET} {center_z:.4f}" '
          f'axisangle="{axis_angle_val}" material="wood"/>')
    
    # Update edge coordinates for the next ramp segment
    current_x += dx
    current_z += dz


# ==========================================
# 3. RANDOM UNEVEN TERRAIN (LANE 3)
# ==========================================
print('\n')
RUBBLE_Y_OFFSET = 2.0

area_length = 15.0      # How far down the X-axis the rubble goes
min_height = 0.005      # 0.5 cm
max_height = 0.10       # 10 cm
block_size_xy = 0.1     # 10x10 cm footprint per block
position_noise = 0.02   # Random X/Y scatter
rotation_noise = 15.0   # Random Yaw rotation

num_rows = int(area_length / block_size_xy)
num_cols = int(LANE_WIDTH / block_size_xy)

# Start Y so the grid is centered on RUBBLE_Y_OFFSET
start_y = RUBBLE_Y_OFFSET - (LANE_WIDTH / 2.0)
geom_count = 0

for i in range(num_rows):
    for j in range(num_cols):
        geom_count += 1
        
        # Base Grid
        x_base = START_X + (i * block_size_xy) + (block_size_xy / 2)
        y_base = start_y + (j * block_size_xy) + (block_size_xy / 2)
        
        # Add Jitter
        x_pos = x_base + random.uniform(-position_noise, position_noise)
        y_pos = y_base + random.uniform(-position_noise, position_noise)
        
        # Random Height
        full_height = random.uniform(min_height, max_height)
        z_size = full_height / 2.0
        
        # Random Rotation
        yaw = math.radians(random.uniform(-rotation_noise, rotation_noise))
        axis_angle_str = f"0 0 1 {yaw:.3f}"
        
        print(f'    <geom name="rubble_{geom_count}" type="box" '
              f'size="{block_size_xy/2:.3f} {block_size_xy/2:.3f} {z_size:.4f}" '
              f'pos="{x_pos:.3f} {y_pos:.3f} {z_size:.4f}" '
              f'axisangle="{axis_angle_str}" material="wood" mass="0.1"/>')

print('\n')
print('')
print('')