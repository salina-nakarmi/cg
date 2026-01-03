import pygame
import math
import numpy as np

# Initialize
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Arbitrary Axis Rotation")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
GRAY = (100, 100, 100)

# Camera parameters
camera_distance = 10
rotation_x = 30  # Pitch (up/down rotation)
rotation_y = 45  # Yaw (left/right rotation)
scale = 100       # Zoom level

def rotate_point(point, rot_x, rot_y):
    """
    Rotate a 3D point based on camera angles
    
    Parameters:
    - point: (x, y, z) tuple
    - rot_x: rotation around X-axis in degrees (pitch)
    - rot_y: rotation around Y-axis in degrees (yaw)
    
    Returns: rotated (x, y, z)
    """
    x, y, z = point
    
    # Convert to radians
    angle_x = math.radians(rot_x)
    angle_y = math.radians(rot_y)
    
    # Rotate around Y-axis (yaw)
    cos_y = math.cos(angle_y)
    sin_y = math.sin(angle_y)
    temp_x = x * cos_y - z * sin_y
    temp_z = x * sin_y + z * cos_y
    x, z = temp_x, temp_z
    
    # Rotate around X-axis (pitch)
    cos_x = math.cos(angle_x)
    sin_x = math.sin(angle_x)
    temp_y = y * cos_x - z * sin_x
    temp_z = y * sin_x + z * cos_x
    y, z = temp_y, temp_z
    
    return (x, y, z)

def project_3d(point):
    """
    Project 3D point to 2D screen coordinates with perspective
    
    Parameters:
    - point: (x, y, z) tuple in 3D space
    
    Returns: (screen_x, screen_y, depth) tuple
    """
    # First rotate based on camera
    x, y, z = rotate_point(point, rotation_x, rotation_y)
    
    # Move away from camera
    z = z + camera_distance
    
    # Avoid division by zero
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

def draw_axes():
    """Draw X, Y, Z coordinate axes"""
    origin = (0, 0, 0)
    axis_length = 5
    
    # X-axis (Red)
    draw_line_3d(origin, (axis_length, 0, 0), RED, 3)
    # Y-axis (Green)
    draw_line_3d(origin, (0, axis_length, 0), GREEN, 3)
    # Z-axis (Blue)
    draw_line_3d(origin, (0, 0, axis_length), BLUE, 3)
    
    # Draw labels
    font = pygame.font.Font(None, 32)
    
    # X label
    p = project_3d((axis_length + 0.5, 0, 0))
    text = font.render('X', True, RED)
    screen.blit(text, (p[0], p[1]))
    
    # Y label
    p = project_3d((0, axis_length + 0.5, 0))
    text = font.render('Y', True, GREEN)
    screen.blit(text, (p[0], p[1]))
    
    # Z label
    p = project_3d((0, 0, axis_length + 0.5))
    text = font.render('Z', True, BLUE)
    screen.blit(text, (p[0], p[1]))

# ===== MAIN LOOP =====
running = True
while running:
    # Handle events
    keys = pygame.key.get_pressed()
    
    # Camera controls
    if keys[pygame.K_w]:
        rotation_x += 2
    if keys[pygame.K_s]:
        rotation_x -= 2
    if keys[pygame.K_a]:
        rotation_y -= 2
    if keys[pygame.K_d]:
        rotation_y += 2
    if keys[pygame.K_q]:
        scale = min(200, scale + 5)  # Zoom in
    if keys[pygame.K_e]:
        scale = max(50, scale - 5)   # Zoom out
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset camera
                rotation_x = 30
                rotation_y = 45
                scale = 100
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw coordinate axes
    draw_axes()
    
    # Display info
    font = pygame.font.Font(None, 24)
    info_lines = [
        f"Camera: Pitch={rotation_x}° Yaw={rotation_y}° Zoom={scale}",
        "Controls: W/S (pitch) A/D (yaw) Q/E (zoom) R (reset)"
    ]
    y_pos = 10
    for line in info_lines:
        text = font.render(line, True, WHITE)
        screen.blit(text, (10, y_pos))
        y_pos += 25
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
