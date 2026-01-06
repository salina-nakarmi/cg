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

# Camera parameters
camera_distance = 10
rotation_x = 30  # Pitch (up/down)
rotation_y = -45  # Yaw (left/right) - CHANGED to negative for proper initial view
scale = 80       # Zoom level

# View modes
VIEW_3D = 0
VIEW_YZ = 1  # Looking down X-axis
VIEW_XZ = 2  # Looking down Y-axis
VIEW_XY = 3  # Looking down Z-axis
current_view = VIEW_3D

def set_view_mode(mode):
    """Set camera to specific view mode"""
    global rotation_x, rotation_y, current_view
    current_view = mode
    
    if mode == VIEW_3D:
        rotation_x = 30
        rotation_y = -45  # CHANGED: negative to get proper default view
    elif mode == VIEW_YZ:  # Look down X-axis
        rotation_x = 0
        rotation_y = -90  # CHANGED: negative
    elif mode == VIEW_XZ:  # Look down Y-axis
        rotation_x = 90
        rotation_y = 0
    elif mode == VIEW_XY:  # Look down Z-axis (looking into screen)
        rotation_x = 0
        rotation_y = 180  # CHANGED: 180 to look from front

def rotate_point(point, rot_x, rot_y):
    """
    Rotate a 3D point based on camera angles
    
    This simulates camera rotation by rotating the world in opposite direction
    - rot_x: pitch (rotation around X-axis)
    - rot_y: yaw (rotation around Y-axis)
    
    RIGHT-HANDED coordinate system:
    - X-axis points RIGHT
    - Y-axis points UP
    - Z-axis points OUTWARD (toward viewer)
    
    Returns: (x, y, z) after rotation
    """
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

def draw_point_3d(point, color, size=6, label=""):
    """Draw a 3D point with optional label"""
    p = project_3d(point)
    pygame.draw.circle(screen, color, (p[0], p[1]), size)
    
    if label:
        font = pygame.font.Font(None, 28)
        text = font.render(label, True, color)
        screen.blit(text, (p[0] + 12, p[1] - 12))

def draw_grid():
    """Draw grid on XZ plane (ground) - DISABLED"""
    # Grid removed as per user request
    pass

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
    draw_line_3d(origin, (0, -axis_length, 0), GREEN, 4)    # Y-axis (UP)
    draw_line_3d(origin, (0, 0, axis_length), BLUE, 4)     # Z-axis (OUTWARD)
    
    # Add labels at the end of each axis
    font = pygame.font.Font(None, 36)
    
    # X label
    p = project_3d((axis_length + 0.5, 0, 0))
    text = font.render('X', True, RED)
    screen.blit(text, (p[0], p[1]))
    
    # Y label
    p = project_3d((0, -(axis_length + 0.5), 0))
    text = font.render('Y', True, GREEN)
    screen.blit(text, (p[0], p[1]))
    
    # Z label
    p = project_3d((0, 0, axis_length + 0.5))
    text = font.render('Z', True, BLUE)
    screen.blit(text, (p[0], p[1]))

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

def draw_ui():
    """Draw user interface panel with instructions and info"""
    panel_x = 10
    panel_y = 10
    
    # Title
    font_title = pygame.font.Font(None, 32)
    title = font_title.render("3D Arbitrary Axis Rotation Visualizer", True, WHITE)
    screen.blit(title, (panel_x, panel_y))
    panel_y += 40
    
    # View mode
    font = pygame.font.Font(None, 24)
    view_names = ["3D Perspective", "YZ Plane (X-axis view)", "XZ Plane (Y-axis view)", "XY Plane (Z-axis view)"]
    view_text = font.render(f"View: {view_names[current_view]}", True, LIGHT_BLUE)
    screen.blit(view_text, (panel_x, panel_y))
    panel_y += 30
    
    # Camera info
    info_text = font.render(f"Camera: Pitch={rotation_x:.0f}° Yaw={rotation_y:.0f}° Zoom={scale}", True, GRAY)
    screen.blit(info_text, (panel_x, panel_y))
    panel_y += 30
    
    # Controls section
    control_y = HEIGHT - 200
    
    # Background box
    pygame.draw.rect(screen, (20, 20, 20), (panel_x - 5, control_y - 5, 500, 190), border_radius=5)
    pygame.draw.rect(screen, (80, 80, 80), (panel_x - 5, control_y - 5, 500, 190), 2, border_radius=5)
    
    font_control = pygame.font.Font(None, 28)
    controls_title = font_control.render("Controls:", True, YELLOW)
    screen.blit(controls_title, (panel_x, control_y))
    control_y += 35
    
    controls = [
        "K/J: Pitch (rotate up/down)",
        "H/L: Yaw (rotate left/right)",
        "Q/E: Zoom in/out",
        "1/2/3/4: Switch view (YZ/XZ/XY/3D)",
        "R: Reset camera",
        "ESC: Quit"
    ]
    
    for control in controls:
        text = font.render(control, True, WHITE)
        screen.blit(text, (panel_x, control_y))
        control_y += 25
    
    # Legend
    # legend_x = WIDTH - 300
    # legend_y = 10
    
    # pygame.draw.rect(screen, (20, 20, 20), (legend_x - 10, legend_y - 10, 290, 180), border_radius=5)
    # pygame.draw.rect(screen, (80, 80, 80), (legend_x - 10, legend_y - 10, 290, 180), 2, border_radius=5)
    
    # legend_title = font_control.render("Legend:", True, WHITE)
    # screen.blit(legend_title, (legend_x, legend_y))
    # legend_y += 35
    
    # legend_items = [
    #     ("Red: X-axis (RIGHT)", RED),
    #     ("Green: Y-axis (UP)", GREEN),
    #     ("Blue: Z-axis (OUTWARD)", BLUE),
    #     ("Yellow: Rotation axis", YELLOW),
    #     ("Orange: Axis points (P₁, P₂)", ORANGE),
    # ]
    
    # for label, color in legend_items:
    #     text = font.render(label, True, color)
    #     screen.blit(text, (legend_x, legend_y))
    #     legend_y += 25

# ========================================
# MAIN LOOP
# ========================================

# Define arbitrary axis points
P1 = (1, -0.5, 1.5)
P2 = (3, -2, -2.5)

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
        scale = min(250, scale + 3)
    if keys[pygame.K_e]:
        scale = max(30, scale - 3)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Reset camera
                rotation_x = 30
                rotation_y = -45  # CHANGED to match initial view
                scale = 80
                current_view = VIEW_3D
            elif event.key == pygame.K_1:
                set_view_mode(VIEW_YZ)
            elif event.key == pygame.K_2:
                set_view_mode(VIEW_XZ)
            elif event.key == pygame.K_3:
                set_view_mode(VIEW_XY)
            elif event.key == pygame.K_4:
                set_view_mode(VIEW_3D)
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw scene
    draw_grid()
    draw_coordinate_planes()
    draw_axes()
    draw_arbitrary_axis(P1, P2)
    
    # Draw UI
    draw_ui()
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()