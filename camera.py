"""
Camera System
Handles smooth camera following, leading, screen shake, and bounds
"""

import pygame
import random
import math
from constants import *


class Camera:
    """Camera that follows the player smoothly"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0

        # Screen shake
        self.shake_amount = 0
        self.shake_x = 0
        self.shake_y = 0

        # Level bounds
        self.min_x = 0
        self.max_x = 10000  # Will be set by level
        self.min_y = 0
        self.max_y = 10000

        # Camera leading (look ahead in direction player is facing)
        self.lead_x = 0
        self.target_lead_x = 0

    def set_bounds(self, min_x, max_x, min_y, max_y):
        """Set camera boundaries based on level size"""
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def update(self, target_x, target_y, target_facing=0):
        """
        Update camera position to follow target
        target_x, target_y: position to follow
        target_facing: -1 for left, 1 for right (for camera leading)
        """
        # Calculate target camera position (centered on target)
        self.target_x = target_x - SCREEN_WIDTH // 2
        self.target_y = target_y - SCREEN_HEIGHT // 2

        # Camera leading - look ahead in the direction the player is facing
        self.target_lead_x = target_facing * CAMERA_LEAD_DISTANCE
        self.lead_x += (self.target_lead_x - self.lead_x) * CAMERA_LERP_SPEED * 0.5

        # Add leading offset
        self.target_x += self.lead_x

        # Smoothly interpolate to target (lerp)
        self.x += (self.target_x - self.x) * CAMERA_LERP_SPEED
        self.y += (self.target_y - self.y) * CAMERA_LERP_SPEED

        # Clamp to bounds
        self.x = max(self.min_x, min(self.x, self.max_x - self.width))
        self.y = max(self.min_y, min(self.y, self.max_y - self.height))

        # Update screen shake
        if self.shake_amount > 0:
            self.shake_x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_y = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_amount *= CAMERA_SHAKE_DECAY
            if self.shake_amount < 0.5:
                self.shake_amount = 0
                self.shake_x = 0
                self.shake_y = 0

    def add_shake(self, amount=10):
        """Add screen shake effect"""
        self.shake_amount = max(self.shake_amount, amount)

    def get_offset(self):
        """Get camera offset including shake"""
        return (int(self.x + self.shake_x), int(self.y + self.shake_y))

    def apply(self, rect):
        """Apply camera offset to a rect"""
        offset = self.get_offset()
        return pygame.Rect(rect.x - offset[0], rect.y - offset[1],
                          rect.width, rect.height)

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        offset = self.get_offset()
        return (x - offset[0], y - offset[1])

    def screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates"""
        offset = self.get_offset()
        return (x + offset[0], y + offset[1])

    def is_visible(self, rect, margin=100):
        """Check if a rectangle is visible on screen (with margin)"""
        offset = self.get_offset()
        screen_rect = pygame.Rect(-margin, -margin,
                                  SCREEN_WIDTH + margin * 2,
                                  SCREEN_HEIGHT + margin * 2)
        object_rect = pygame.Rect(rect.x - offset[0], rect.y - offset[1],
                                  rect.width, rect.height)
        return screen_rect.colliderect(object_rect)


class ParallaxBackground:
    """Parallax scrolling background for depth effect"""

    def __init__(self):
        self.layers = []
        self._create_layers()

    def _create_layers(self):
        """Create background layers with different scroll speeds"""
        # Layer 1: Far mountains (slowest)
        self.layers.append({
            'speed': 0.2,
            'color': (100, 120, 150),
            'y_offset': SCREEN_HEIGHT - 400,
            'height': 200,
            'type': 'mountains'
        })

        # Layer 2: Mid hills
        self.layers.append({
            'speed': 0.4,
            'color': (120, 140, 170),
            'y_offset': SCREEN_HEIGHT - 300,
            'height': 150,
            'type': 'hills'
        })

        # Layer 3: Near trees (fastest)
        self.layers.append({
            'speed': 0.6,
            'color': (80, 100, 120),
            'y_offset': SCREEN_HEIGHT - 200,
            'height': 100,
            'type': 'trees'
        })

    def draw(self, screen, camera_offset):
        """Draw parallax background layers"""
        # Draw sky gradient
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            color = (
                int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * progress),
                int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * progress),
                int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * progress)
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        # Draw each layer
        for layer in self.layers:
            offset_x = camera_offset[0] * layer['speed']
            y_pos = layer['y_offset']

            if layer['type'] == 'mountains':
                self._draw_mountains(screen, offset_x, y_pos, layer)
            elif layer['type'] == 'hills':
                self._draw_hills(screen, offset_x, y_pos, layer)
            elif layer['type'] == 'trees':
                self._draw_trees(screen, offset_x, y_pos, layer)

    def _draw_mountains(self, screen, offset_x, y_pos, layer):
        """Draw mountain silhouettes"""
        points = []
        num_peaks = 8
        width_per_peak = SCREEN_WIDTH * 2 // num_peaks

        for i in range(num_peaks + 2):
            x = i * width_per_peak - (offset_x % (width_per_peak * num_peaks))
            height = random.randint(100, layer['height'])
            points.append((x, y_pos + layer['height'] - height))

        # Add bottom corners
        points.append((SCREEN_WIDTH, SCREEN_HEIGHT))
        points.append((0, SCREEN_HEIGHT))

        if len(points) > 2:
            pygame.draw.polygon(screen, layer['color'], points)

    def _draw_hills(self, screen, offset_x, y_pos, layer):
        """Draw rolling hills"""
        points = [(0, SCREEN_HEIGHT)]

        for x in range(-200, SCREEN_WIDTH + 200, 50):
            wave_x = (x + offset_x) * 0.01
            wave_height = math.sin(wave_x) * 30
            points.append((x - offset_x % 100, y_pos + wave_height))

        points.append((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.draw.polygon(screen, layer['color'], points)

    def _draw_trees(self, screen, offset_x, y_pos, layer):
        """Draw simple tree silhouettes"""
        tree_spacing = 150
        tree_width = 40

        for i in range(-2, SCREEN_WIDTH // tree_spacing + 2):
            x = i * tree_spacing - int(offset_x % (tree_spacing * 10))
            tree_height = random.randint(60, 100)

            # Tree trunk
            trunk_rect = pygame.Rect(x - tree_width // 4, y_pos,
                                    tree_width // 2, tree_height)
            pygame.draw.rect(screen, layer['color'], trunk_rect)

            # Tree foliage (triangle)
            points = [
                (x, y_pos - 20),
                (x - tree_width // 2, y_pos + tree_height // 2),
                (x + tree_width // 2, y_pos + tree_height // 2)
            ]
            pygame.draw.polygon(screen, layer['color'], points)
