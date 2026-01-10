import pygame
import math
import numpy as np

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Arbitrary Axis Rotation - Educational Visualizer")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)

# Camera parameters
camera_distance = 10
rotation_x = 350  # Pitch (up/down)
rotation_y = -241  # Yaw (left/right) - CHANGED to negative for proper initial view
scale = 250       # Zoom level

# View modes
VIEW_3D = 0
VIEW_YZ = 1  # Looking down X-axis
VIEW_XZ = 2  # Looking down Y-axis
VIEW_XY = 3  # Looking down Z-axis
current_view = VIEW_3D

# Transformation steps
STEP_0_ORIGINAL = 0
STEP_1_TRANSLATE = 1
STEP_2_ROTATE_Z = 2
STEP_3_ROTATE_Y = 3
STEP_4_ROTATE_X = 4
STEP_5_INVERSE = 5
current_step = 0

# Animation
theta = 0  # Current rotation angle
paused = True
show_angles = True
show_vector = True #toggle for showing positional vectors

def set_view_mode(mode):
    """Set camera to specific view mode"""
    global rotation_x, rotation_y, current_view
    current_view = mode
    
    if mode == VIEW_3D:
        rotation_x = 350
        rotation_y = -241  # CHANGED: negative to get proper default view
    elif mode == VIEW_YZ:  # Look down X-axis
        rotation_x = 0
        rotation_y = 90  # CHANGED: negative
    elif mode == VIEW_XZ:  # Look down Y-axis
        rotation_x = 90
        rotation_y = 0
    elif mode == VIEW_XY:  # Look down Z-axis (looking into screen)
        rotation_x = 0
        rotation_y = 180  # CHANGED: 180 to look from front

def rotate_point(point, rot_x, rot_y):
    """Rotate a 3D point based on camera angles"""
    x, y, z = point
    
    # Convert degrees to radians
    angle_x = math.radians(rot_x)
    angle_y = math.radians(rot_y)
    
    # Rotate around Y-axis first (yaw)
    # FIXED: Negated sin_y to make X point RIGHT when Z points out
    cos_y = math.cos(angle_y)
    sin_y = math.sin(angle_y)
    temp_x = x * cos_y + z * sin_y  # CHANGED: was (- z * sin_y)
    temp_z = -x * sin_y + z * cos_y  # CHANGED: was (+ z * cos_y)
    x, z = temp_x, temp_z
    
    # Then rotate around X-axis (pitch)
    cos_x = math.cos(angle_x)
    sin_x = math.sin(angle_x)
    temp_y = y * cos_x - z * sin_x
    temp_z = y * sin_x + z * cos_x
    y, z = temp_y, temp_z
    
    return (x, y, z)

def project_3d(point):
    """
    Project 3D point to 2D screen coordinates using perspective projection
    
    Formula: screen_coord = center + (world_coord * scale) / (depth + camera_distance)
    
    This simulates perspective: objects farther away appear smaller
    
    Returns: (screen_x, screen_y, depth)
    """
    # First apply camera rotation
    x, y, z = rotate_point(point, rotation_x, rotation_y)
    
    # Move scene away from camera
    z = z + camera_distance
    
    # Prevent division by zero
    if z <= 0.1:
        z = 0.1
    
    # Perspective projection
    factor = scale / z
    screen_x = int(WIDTH / 2 + x * factor)
    screen_y = int(HEIGHT / 2 - y * factor)  # Negative because screen Y goes down
    
    return (screen_x, screen_y, z)

def draw_line_3d(start, end, color, width=2):
    """Draw a line between two 3D points"""
    p1 = project_3d(start)
    p2 = project_3d(end)
    pygame.draw.line(screen, color, (p1[0], p1[1]), (p2[0], p2[1]), width)

# *** ADDED: New function for drawing arrows ***
def draw_arrow_3d(start, end, color, width=3):
    """Draw an arrow (line with arrowhead) from start to end point"""
    # Draw the main line
    draw_line_3d(start, end, color, width)
    
    # Calculate direction vector
    direction = np.array(end) - np.array(start)
    length = np.linalg.norm(direction)
    
    if length < 0.001:
        return
    
    direction = direction / length
    
    # Create arrowhead
    arrow_size = 0.3
    
    # Find perpendicular vectors
    if abs(direction[0]) < 0.9:
        perp1 = np.cross(direction, [1, 0, 0])
    else:
        perp1 = np.cross(direction, [0, 1, 0])
    perp1 = perp1 / np.linalg.norm(perp1)
    perp2 = np.cross(direction, perp1)
    
    # Arrowhead base
    arrow_base = np.array(end) - direction * arrow_size
    
    # Arrowhead points
    arrow_p1 = arrow_base + perp1 * arrow_size * 0.5
    arrow_p2 = arrow_base - perp1 * arrow_size * 0.5
    arrow_p3 = arrow_base + perp2 * arrow_size * 0.5
    arrow_p4 = arrow_base - perp2 * arrow_size * 0.5
    
    # Draw arrowhead
    draw_line_3d(end, tuple(arrow_p1), color, max(1, width-1))
    draw_line_3d(end, tuple(arrow_p2), color, max(1, width-1))
    draw_line_3d(end, tuple(arrow_p3), color, max(1, width-1))
    draw_line_3d(end, tuple(arrow_p4), color, max(1, width-1))

def draw_point_3d(point, color, size=6, label=""):
    """Draw a 3D point with optional label"""
    p = project_3d(point)
    pygame.draw.circle(screen, color, (p[0], p[1]), size)
    
    if label:
        font = pygame.font.Font(None, 28)
        text = font.render(label, True, color)
        screen.blit(text, (p[0] + 12, p[1] - 12))
    

def draw_plane_3d(corners, color, alpha=60):
    """
    Draw a semi-transparent plane
    
    corners: list of 4 3D points defining plane corners
    color: RGB tuple
    alpha: transparency (0=invisible, 255=opaque)
    """
    # Project all corners to 2D
    projected = [project_3d(c) for c in corners]
    
    # Create transparent surface
    plane_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Draw filled polygon
    points_2d = [(p[0], p[1]) for p in projected]
    pygame.draw.polygon(plane_surface, (*color, alpha), points_2d)
    
    # Draw border
    for i in range(len(points_2d)):
        next_i = (i + 1) % len(points_2d)
        pygame.draw.line(plane_surface, (*color, 150), points_2d[i], points_2d[next_i], 2)
    
    # Blit to main screen
    screen.blit(plane_surface, (0, 0))
    
    # Return average depth for sorting
    avg_z = sum(p[2] for p in projected) / len(projected)
    return avg_z

def draw_coordinate_planes():
    """
    Draw the three coordinate planes: XY, XZ, YZ
    With transparency and proper depth sorting
    """
    plane_size = 6  # INCREASED from 4 to 6 for bigger planes
    planes = []
    
    # XY Plane (z=0) - Light cyan
    xy_corners = [
        (-plane_size, -plane_size, 0),
        (plane_size, -plane_size, 0),
        (plane_size, plane_size, 0),
        (-plane_size, plane_size, 0)
    ]
    planes.append((xy_corners, (150, 220, 220)))
    
    # XZ Plane (y=0) - Light tan
    xz_corners = [
        (-plane_size, 0, -plane_size),
        (plane_size, 0, -plane_size),
        (plane_size, 0, plane_size),
        (-plane_size, 0, plane_size)
    ]
    planes.append((xz_corners, (220, 200, 150)))
    
    # YZ Plane (x=0) - Light green
    yz_corners = [
        (0, -plane_size, -plane_size),
        (0, plane_size, -plane_size),
        (0, plane_size, plane_size),
        (0, -plane_size, plane_size)
    ]
    planes.append((yz_corners, (200, 220, 180)))
    
    # Calculate depth for each plane and sort (painter's algorithm)
    plane_depths = []
    for corners, color in planes:
        projected = [project_3d(c) for c in corners]
        avg_z = sum(p[2] for p in projected) / len(projected)
        plane_depths.append((avg_z, corners, color))
    
    # Sort by depth (draw farthest first)
    plane_depths.sort(reverse=True)
    
    # Draw planes in order
    for _, corners, color in plane_depths:
        draw_plane_3d(corners, color, alpha=50)

def draw_axes():
    """
    Draw coordinate axes with labels
    RIGHT-HANDED coordinate system:
    X-axis: Red (points RIGHT)
    Y-axis: Green (points UP)
    Z-axis: Blue (points OUTWARD toward viewer)
    """
    origin = (0, 0, 0)
    axis_length = 6  # INCREASED from 5 to 6
    
    # Draw axes as thick lines
    draw_line_3d(origin, (axis_length, 0, 0), RED, 4)      # X-axis (RIGHT)
    draw_line_3d(origin, (0, axis_length, 0), GREEN, 4)    # Y-axis (UP)
    draw_line_3d(origin, (0, 0, axis_length), BLUE, 4)     # Z-axis (OUTWARD)
    
    # Add labels at the end of each axis
    font = pygame.font.Font(None, 36)
    
    # X label
    p = project_3d((axis_length + 0.5, 0, 0))
    text = font.render('X', True, RED)
    screen.blit(text, (p[0], p[1]))
    
    # Y label
    p = project_3d((0, (axis_length + 0.5), 0))
    text = font.render('Y', True, GREEN)
    screen.blit(text, (p[0], p[1]))
    
    # Z label
    p = project_3d((0, 0, axis_length + 0.5))
    text = font.render('Z', True, BLUE)
    screen.blit(text, (p[0], p[1]))

# ------------------------------------------------------------------------
def draw_arc_3d(center, radius, start_angle, end_angle, normal, color, width=3, segments=20):
    """Draw an arc in 3D space to visualize angles"""
    normal = np.array(normal)
    norm = np.linalg.norm(normal)
    if norm < 0.001:
        return
    normal = normal / norm
    
    # Find perpendicular vectors
    if abs(normal[0]) < 0.9:
        perp1 = np.cross(normal, [1, 0, 0])
    else:
        perp1 = np.cross(normal, [0, 1, 0])
    perp1 = perp1 / np.linalg.norm(perp1)
    perp2 = np.cross(normal, perp1)
    
    points = []
    for i in range(segments + 1):
        angle = start_angle + (end_angle - start_angle) * i / segments
        x = center[0] + radius * (math.cos(angle) * perp1[0] + math.sin(angle) * perp2[0])
        y = center[1] + radius * (math.cos(angle) * perp1[1] + math.sin(angle) * perp2[1])
        z = center[2] + radius * (math.cos(angle) * perp1[2] + math.sin(angle) * perp2[2])
        points.append((x, y, z))
    
    for i in range(len(points) - 1):
        draw_line_3d(points[i], points[i+1], color, width)

# ---------------------------------------------------------------------------

def normalize_vector(v):
    """Normalize a vector to unit length"""
    norm = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if norm < 1e-10:
        return (1,0,0) # Default to X-axis if zero vector
    return (v[0]/norm, v[1]/norm, v[2]/norm)

def apply_transformation(point, matrix):
    """Apply a 4x4 transformation matrix to a  point"""
    p = np.array([point[0], point[1], point[2], 1])
    result = matrix @ p #Series of matirx multiplication
    return (result[0], result[1], result[2])

def translation_matrix(tx, ty, tz):
    """Create translation matrix"""
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ], dtype=float)

def rotation_z_matrix(angle):
    """Create rotation matrix around Z-axis"""
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def rotation_y_matrix(angle):
    """Create rotation matrix around Y-axis"""
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ], dtype=float)

def rotation_x_matrix(angle):
    """Create rotation matrix around Z-axis"""
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ], dtype=float)

# ---------------------------------------------------------------------------

# Transfromation Steps:

def step_0_original(point, p1, p2):
    """Original point (no transformation)"""
    return point, p1, p2, None

def step_1_translate(point, p1, p2):
    """Translate so that P1 is at origin"""
    tx, ty, tz = -p1[0], -p1[1], -p1[2]
    T = translation_matrix(tx, ty, tz)
    new_point = apply_transformation(point, T)
    new_p1 = (0,0,0)
    new_p2 = apply_transformation(p2, T)
    return new_point, new_p1, new_p2, {'T': (tx, ty, tz)}

def step_2_rotate_z(point, p1, p2):
    """Rotate around Z-axis to align P2 with XZ plane"""
    #  First apply step 1
    point, p1, p2, _ = step_1_translate(point, p1, p2)

    #Calculate alpha
    a, b, c = normalize_vector(p2)
    d = math.sqrt(a*a + b*b) #cause viewed from z axis in the XY plane

    if d > 1e-10:
        cos_alpha = a / d
        sin_alpha = b / d
        alpha = math.atan2(sin_alpha, cos_alpha)
    else:
        alpha = 0
    
    #Apply Rz(-alpha)
    Rz = rotation_z_matrix(-alpha)
    new_point = apply_transformation(point, Rz)
    new_p2 = apply_transformation(p2, Rz)

    return new_point, P1, new_p2, {'alpha': alpha, 'd': d, 'a': a, 'b': b, 'c': c}


def step_3_rotate_y(point, p1, p2):
    """Step 3: Rotate about Y-axis to align with X-axis"""
    # Apply steps 1 and 2
    point, p1, p2, info = step_2_rotate_z(point, p1, p2)
    alpha, d, a, b, c = info['alpha'], info['d'], info['a'], info['b'], info['c']
    
    # Calculate beta
    cos_beta = d
    sin_beta = c
    beta = math.atan2(sin_beta, cos_beta)
    
    # Apply Ry(-beta)
    Ry = rotation_y_matrix(-beta)
    new_point = apply_transformation(point, Ry)
    new_p2 = apply_transformation(p2, Ry)
    
    return new_point, p1, new_p2, {'alpha': alpha, 'beta': beta, 'd': d, 'a': a, 'b': b, 'c': c}

def step_4_rotate_x(point, p1, p2, theta):
    """Step 4: Rotate about X-axis by angle theta"""
    #Apply step 1,2,3
    point, p1, p2, info = step_3_rotate_y(point, p1, p2)

    # Apply Rx(theta)
    Rx = rotation_x_matrix(theta)
    new_point = apply_transformation(point, Rx)

    return new_point, p1, p2, info

def step_5_inverse(point, p1_orig, p2_orig, theta):
    """Step 5: Apply inverse transformations"""
    # Get to step 4
    point, _, _, info = step_4_rotate_x(point, p1_orig, p2_orig, theta)
    alpha, beta = info['alpha'], info['beta']
    
    # Apply inverse: Ry(beta), Rx(alpha), Translate back
    Ry_inv = rotation_y_matrix(beta)
    Rz_inv = rotation_z_matrix(alpha)
    T_inv = translation_matrix(p1_orig[0], p1_orig[1], p1_orig[2])
    
    new_point = apply_transformation(point, Ry_inv)
    new_point = apply_transformation(new_point, Rz_inv)
    new_point = apply_transformation(new_point, T_inv)
    
    return new_point, p1_orig, p2_orig, {'alpha': alpha, 'beta': beta}

#-----------------------------------------------------------------------------------------------------------



def draw_arbitrary_axis(p1, p2):
    """
    Draw the arbitrary rotation axis
    
    p1, p2: two points defining the axis
    Draws as a bright yellow line extending beyond the points
    """
    # Calculate direction and extend the line
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    
    # Normalize
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length > 0.001:
        dx, dy, dz = dx/length, dy/length, dz/length
    
    # Extend line in both directions
    extend = 4
    start = (p1[0] - dx*extend, p1[1] - dy*extend, p1[2] - dz*extend)
    end = (p2[0] + dx*extend, p2[1] + dy*extend, p2[2] + dz*extend)
    
    # Draw extended axis line
    draw_line_3d(start, end, YELLOW, 6)
    
    # Draw points P1 and P2
    draw_point_3d(p1, ORANGE, 10, "P1")
    draw_point_3d(p2, ORANGE, 10, "P2")

def draw_cube(center, size, color):
    """Draw a cube at given center"""
    half = size / 2
    vertices = [
        (center[0]-half, center[1]-half, center[2]-half),
        (center[0]+half, center[1]-half, center[2]-half),
        (center[0]+half, center[1]+half, center[2]-half),
        (center[0]-half, center[1]+half, center[2]-half),
        (center[0]-half, center[1]-half, center[2]+half),
        (center[0]+half, center[1]-half, center[2]+half),
        (center[0]+half, center[1]+half, center[2]+half),
        (center[0]-half, center[1]+half, center[2]+half)
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    for edge in edges:
        draw_line_3d(vertices[edge[0]], vertices[edge[1]], color, 3)
    
    for vertex in vertices:
        draw_point_3d(vertex, color, 4)

def draw_step_info():
    """Draw information panel for current step"""
    panel_x =10
    panel_y = 10

    font_title = pygame.font.Font(None, 32)
    font = pygame.font.Font(None, 24)

    #Title
    title = font_title.render("Transformation Step Info", True, WHITE)
    screen.blit(title, (panel_x, panel_y))
    panel_y += 40

    # Currwnt step
    step_names = [
        "Step 0 : Original - Initial Configuration",
        "Step 1 : Translation - Move P1 to Origin",
        "Step 2 : Rotate Z - Align P2 with XZ Plane (α)", 
        "Step 3 : Rotate Y - Align P2 with X-axis (β)",
        "Step 4 : Rotate X - Apply Rotation around X-axis (θ)",
        "Step 5 : Inverse - Return to Original Position with inverse transmormation"
    ]

    step_text = font_title.render(step_names[current_step], True, LIGHT_BLUE)
    screen.blit(step_text, (panel_x, panel_y))
    panel_y += 40

    #Step-specific info
    if current_step == STEP_0_ORIGINAL:
        lines = [
            f"Rotation axis from P1 to P2",
            f"P1 = ({P1[0]:.2f}, {P1[1]:.2f}, {P1[2]:.2f})",
            f"P2 = ({P2[0]:.2f}, {P2[1]:.2f}, {P2[2]:.2f})",
            f"Test point P = ({test_point[0]:.2f}, {test_point[1]:.2f}, {test_point[2]:.2f})",
            "",
            "This axis is NOT parallel to any coordinate axis!"
        ]
    elif current_step == STEP_1_TRANSLATE:
        _, _, _, info = step_1_translate(test_point, P1, P2)
        lines = [
            f"Translation vector: T = {info['T'][0]:.2f}",
            f"New P1 = (0, 0, 0)",
            "",
            "Why? Rotations are simpler when axis",
            "passes through the origin."
        ]
    elif current_step == STEP_2_ROTATE_Z:
        _, _, _, info = step_2_rotate_z(test_point, P1, P2)
        alpha_deg = math.degrees(info['alpha'])
        lines = [
            f"Axis unit vector: ({info['a']:.3f}, {info['b']:.3f}, {info['c']:.3f})",
            f"d = √(a² +b²) = {info['d']:.3f}",
            f"α = arctan(b/a) = {alpha_deg:.1f}°",
            "",
            "Rotate about Z-axis by -α",
            "Result: Axis now in XZ plane (y = 0)"
        ]
    elif current_step == STEP_3_ROTATE_Y:
        _, _, _, info = step_3_rotate_y(test_point, P1, P2)
        beta_deg = math.degrees(info['beta'])
        lines = [
            f"β = arctan(c/d) = {beta_deg:.1f}°",
            f"cos(β) = d = {info['d']:.3f}",
            f"sin(β) = c = {info['a']:.3f}",
            "",
            "Rotate about Y-axis by -β",
            "Result: Axis aligned with X-axis"
        ]
    elif current_step == STEP_4_ROTATE_X:
        theta_deg = math.degrees(theta)
        lines = [
            f"Rotate angle: θ = {theta_deg:.1f}°",
            "",
            "Rotate about X-axis by θ",
            "This is our DESIRED rotation!",
            "",
            "Point rotates in YZ plane around X-axis"
        ]
    else:
        _, _, _, info = step_5_inverse(test_point, P1, P2, theta)
        lines = [
            "Apply inverse transformations:",
            f"1. Ry(+β) where β = {math.degrees(info['beta']):.1f}°",
            f"2. Rz(+α) where α = {math.degrees(info['alpha']):.1f}°",
            f"3. Translate by +({P1[0]:.2f}, {P1[1]:.2f}, {P1[2]:.2f})",
            "",
            "Final: Point rotated about arbitrary axis!"
        ]

    for line in lines:
        text = font.render(line, True, WHITE)
        screen.blit(text, (panel_x, panel_y))
        panel_y += 25


def draw_controls():
    """Draw control panel"""
    panel_x = 10
    panel_y = HEIGHT - 270
    
    pygame.draw.rect(screen, (20, 20, 20), (panel_x - 5, panel_y - 5, 400, 245), border_radius=5)
    pygame.draw.rect(screen, (80, 80, 80), (panel_x - 5, panel_y - 5, 400, 245), 2, border_radius=5)
    
    font_title = pygame.font.Font(None, 28)
    font = pygame.font.Font(None, 24)
    
    title = font_title.render("Controls:", True, YELLOW)
    screen.blit(title, (panel_x, panel_y))
    panel_y += 35
    
    controls = [
        "SPACE: Play/Pause rotation",
        "← →: Previous/Next step",
        "K/J: Pitch camera (up/down)",
        "H/L: Yaw camera (left/right)",
        "Q/E: Zoom in/out",
        "1/2/3/4: View YZ/XZ/XY/3D",
        "R: Reset camera",
        "A: Toggle angle display"
        "V: Toggle position vector" 
    ]
    
    for control in controls:
        text = font.render(control, True, WHITE)
        screen.blit(text, (panel_x, panel_y))
        panel_y += 25

# ========================================
# MAIN LOOP
# ========================================

# Define arbitrary axis points
P1 = (-1, 0.5, 1.5)
P2 = (-3, 2, 2.5)

# Test point to rotate
test_point = (-2.5, 1.5, 0.5)

running = True
while running:
   
    # Event handling
    keys = pygame.key.get_pressed()
    
    # Camera controls (only in 3D view)
    if current_view == VIEW_3D:
        if keys[pygame.K_k]:
            rotation_x += 2
        if keys[pygame.K_j]:
            rotation_x -= 2
        if keys[pygame.K_h]:
            rotation_y -= 2
        if keys[pygame.K_l]:
            rotation_y += 2
    
    # Zoom (works in all views)
    if keys[pygame.K_q]:
        scale = min(350, scale + 3)
    if keys[pygame.K_e]:
        scale = max(150, scale - 3)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:  # *** ADDED: Space to play/pause ***
                paused = not paused
            elif event.key == pygame.K_RIGHT:
                current_step = min(5, current_step + 1)
            elif event.key == pygame.K_LEFT:
                current_step = max(0, current_step - 1)
            elif event.key == pygame.K_r:
                # Reset camera
                rotation_x = 350
                rotation_y = -241  # CHANGED to match initial view
                scale = 250
                current_view = VIEW_3D
            elif event.key == pygame.K_1:
                set_view_mode(VIEW_YZ)
            elif event.key == pygame.K_2:
                set_view_mode(VIEW_XZ)
            elif event.key == pygame.K_3:
                set_view_mode(VIEW_XY)
            elif event.key == pygame.K_4:
                set_view_mode(VIEW_3D)
    
    # Update animation
# *** FIXED: Changed comparison from function to constant ***
    if not paused and current_step >= STEP_4_ROTATE_X:
        theta += 0.02
        if theta > 2 * math.pi:
            theta = 0

    # Clear screen
    screen.fill(BLACK)
    
    # Draw scene
    draw_coordinate_planes()
    draw_axes()

    # apply current transformation
    if current_step == STEP_0_ORIGINAL:
        display_point, display_p1, display_p2, info = step_0_original(test_point, P1, P2)
    elif current_step == STEP_1_TRANSLATE:
        display_point, display_p1, display_p2, info = step_1_translate(test_point, P1, P2)
    elif current_step == STEP_2_ROTATE_Z:
        display_point, display_p1, display_p2, info = step_2_rotate_z(test_point, P1, P2)
    elif current_step == STEP_3_ROTATE_Y:
        display_point, display_p1, display_p2, info = step_3_rotate_y(test_point, P1, P2)
    elif current_step == STEP_4_ROTATE_X:
        display_point, display_p1, display_p2, info = step_4_rotate_x(test_point, P1, P2, theta)
    else:
        display_point, display_p1, display_p2, info = step_5_inverse(test_point, P1, P2, theta)

    # Draw rotation axis
    draw_arbitrary_axis(P1, P2)
    
    # Draw angle arcs
    if show_angles and info:
        if current_step == STEP_2_ROTATE_Z:
            alpha = info['alpha']
            if abs(alpha) > 0.01:
                draw_arc_3d((0, 0, 0), 1.5, 0, alpha, (0, 0, 1), PURPLE, 3, 15)
        elif current_step == STEP_3_ROTATE_Y:
            beta = info['beta']
            if abs(beta) > 0.01:
                draw_arc_3d((0, 0, 0), 1.5, 0, beta, (0, 1, 0), PURPLE, 3, 15)
        elif current_step >= STEP_4_ROTATE_X and theta > 0:
            draw_arc_3d((0, 0, 0), 1.8, 0, theta, (1, 0, 0), MAGENTA, 3, 20)

    # Draw cube at point
    draw_cube(display_point, 0.4, CYAN)
    draw_point_3d(display_point, MAGENTA, 8, "P")

    # Draw UI
    draw_step_info()
    draw_controls()
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()