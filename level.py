"""
Level System
Handles loading levels from JSON and managing level objects
"""

import pygame
import json
import os
from platforms import (Platform, MovingPlatform, FallingPlatform,
                      BouncyPlatform, OneWayPlatform, Hazard, Collectible)
from constants import *


class Level:
    """Manages a single level"""

    def __init__(self, level_number=1):
        self.level_number = level_number
        self.platforms = []
        self.hazards = []
        self.collectibles = []
        self.enemies = []
        self.spawn_point = (100, 100)
        self.width = SCREEN_WIDTH * 3
        self.height = SCREEN_HEIGHT
        self.completed = False
        self.goal = None
        self.checkpoint = None

    def load_from_json(self, filepath):
        """Load level from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.width = data.get('width', SCREEN_WIDTH * 3)
            self.height = data.get('height', SCREEN_HEIGHT)
            self.spawn_point = tuple(data.get('spawn', [100, 100]))

            # Load platforms
            self.platforms = []
            for plat_data in data.get('platforms', []):
                plat = self._create_platform(plat_data)
                if plat:
                    self.platforms.append(plat)

            # Load hazards
            self.hazards = []
            for hazard_data in data.get('hazards', []):
                hazard = Hazard(
                    hazard_data['x'],
                    hazard_data['y'],
                    hazard_data['width'],
                    hazard_data['height'],
                    hazard_data.get('type', 'spike')
                )
                self.hazards.append(hazard)

            # Load collectibles
            self.collectibles = []
            for coll_data in data.get('collectibles', []):
                coll = Collectible(
                    coll_data['x'],
                    coll_data['y'],
                    coll_data.get('type', 'coin')
                )
                self.collectibles.append(coll)

            # Load goal
            goal_data = data.get('goal')
            if goal_data:
                self.goal = {
                    'rect': pygame.Rect(goal_data['x'], goal_data['y'],
                                       goal_data.get('width', 50),
                                       goal_data.get('height', 50))
                }

            # Load checkpoint
            checkpoint_data = data.get('checkpoint')
            if checkpoint_data:
                self.checkpoint = {
                    'rect': pygame.Rect(checkpoint_data['x'], checkpoint_data['y'],
                                       checkpoint_data.get('width', 40),
                                       checkpoint_data.get('height', 60)),
                    'activated': False,
                    'position': (checkpoint_data['x'], checkpoint_data['y'])
                }

            return True

        except FileNotFoundError:
            print(f"Level file not found: {filepath}")
            return False
        except json.JSONDecodeError:
            print(f"Invalid JSON in level file: {filepath}")
            return False

    def _create_platform(self, plat_data):
        """Create appropriate platform type from data"""
        x = plat_data['x']
        y = plat_data['y']
        width = plat_data['width']
        height = plat_data['height']
        plat_type = plat_data.get('type', 'normal')

        if 'pattern' in plat_data:
            # Moving platform
            return MovingPlatform(
                x, y, width, height,
                platform_type=plat_type,
                pattern=plat_data['pattern'],
                speed=plat_data.get('speed', 2),
                distance=plat_data.get('distance', 200)
            )
        elif plat_type == 'fall':
            return FallingPlatform(x, y, width, height)
        elif plat_type == 'bouncy':
            return BouncyPlatform(x, y, width, height)
        elif plat_type == 'oneway':
            return OneWayPlatform(x, y, width, height)
        else:
            return Platform(x, y, width, height, plat_type)

    def create_default(self):
        """Create a simple default level for testing"""
        self.spawn_point = (100, 100)
        self.width = SCREEN_WIDTH * 4
        self.height = SCREEN_HEIGHT

        # Ground
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 50, self.width, 50))

        # Starting platform
        self.platforms.append(Platform(50, 500, 200, 30))

        # Normal platforms
        self.platforms.append(Platform(350, 450, 150, 30))
        self.platforms.append(Platform(600, 400, 150, 30))
        self.platforms.append(Platform(850, 350, 150, 30))

        # Ice platform
        self.platforms.append(Platform(1100, 400, 200, 30, 'ice'))

        # Moving platform
        self.platforms.append(MovingPlatform(1400, 450, 120, 20,
                                            pattern='vertical', speed=2, distance=150))

        # Bouncy platform
        self.platforms.append(BouncyPlatform(1700, 550, 100, 20))

        # Falling platforms
        self.platforms.append(FallingPlatform(2000, 400, 80, 20))
        self.platforms.append(FallingPlatform(2100, 400, 80, 20))
        self.platforms.append(FallingPlatform(2200, 400, 80, 20))

        # One-way platforms
        self.platforms.append(OneWayPlatform(2400, 350, 150, 15))
        self.platforms.append(OneWayPlatform(2400, 500, 150, 15))

        # Wall jump section
        self.platforms.append(Platform(2700, 300, 30, 400))
        self.platforms.append(Platform(2900, 200, 30, 500))

        # Final platform
        self.platforms.append(Platform(3100, 300, 400, 30))

        # Hazards
        self.hazards.append(Hazard(800, SCREEN_HEIGHT - 50 - SPIKE_HEIGHT, 100, SPIKE_HEIGHT))
        self.hazards.append(Hazard(1500, SCREEN_HEIGHT - 50 - SPIKE_HEIGHT, 150, SPIKE_HEIGHT))

        # Collectibles
        for i in range(10):
            x = 400 + i * 300
            y = 300
            self.collectibles.append(Collectible(x, y, 'coin'))

        # Power-up
        self.collectibles.append(Collectible(1200, 300, 'powerup'))

        # Checkpoint
        self.checkpoint = {
            'rect': pygame.Rect(1600, 300, 40, 60),
            'activated': False,
            'position': (1600, 350)
        }

        # Goal
        self.goal = {
            'rect': pygame.Rect(3300, 250, 50, 50)
        }

    def update(self, player):
        """Update all level objects"""
        # Update platforms
        for platform in self.platforms:
            platform.update()

        # Update hazards
        for hazard in self.hazards:
            hazard.update()

        # Update collectibles
        for collectible in self.collectibles:
            collectible.update()

        # Check checkpoint activation
        if self.checkpoint and not self.checkpoint['activated']:
            if player.rect.colliderect(self.checkpoint['rect']):
                self.checkpoint['activated'] = True

        # Check goal
        if self.goal and player.rect.colliderect(self.goal['rect']):
            self.completed = True

    def draw(self, screen, camera_offset):
        """Draw all level objects"""
        # Draw platforms
        for platform in self.platforms:
            if platform.active:
                platform.draw(screen, camera_offset)

        # Draw hazards
        for hazard in self.hazards:
            hazard.draw(screen, camera_offset)

        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(screen, camera_offset)

        # Draw checkpoint
        if self.checkpoint:
            draw_rect = self.checkpoint['rect'].copy()
            draw_rect.x -= camera_offset[0]
            draw_rect.y -= camera_offset[1]

            color = GREEN if self.checkpoint['activated'] else GRAY
            pygame.draw.rect(screen, color, draw_rect)
            pygame.draw.rect(screen, BLACK, draw_rect, 3)

            # Draw flag
            flag_points = [
                (draw_rect.right, draw_rect.top),
                (draw_rect.right, draw_rect.top + 20),
                (draw_rect.right + 30, draw_rect.top + 10)
            ]
            pygame.draw.polygon(screen, color, flag_points)

        # Draw goal
        if self.goal:
            draw_rect = self.goal['rect'].copy()
            draw_rect.x -= camera_offset[0]
            draw_rect.y -= camera_offset[1]

            # Animated goal
            import math
            import pygame
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
            goal_rect = draw_rect.inflate(pulse, pulse)

            pygame.draw.rect(screen, YELLOW, goal_rect)
            pygame.draw.rect(screen, ORANGE, goal_rect, 4)

            # Draw star shape
            center_x = goal_rect.centerx
            center_y = goal_rect.centery
            size = 20

            font = pygame.font.Font(None, 40)
            text = font.render('*', True, ORANGE)
            screen.blit(text, (center_x - 10, center_y - 15))

    def get_active_platforms(self):
        """Get list of active platforms for collision"""
        return [p for p in self.platforms if p.active]

    def get_spawn_point(self):
        """Get the spawn point (checkpoint if activated, otherwise start)"""
        if self.checkpoint and self.checkpoint['activated']:
            return self.checkpoint['position']
        return self.spawn_point

    def reset(self):
        """Reset level state (for retry)"""
        self.completed = False

        # Reset platforms
        for platform in self.platforms:
            platform.active = True
            if isinstance(platform, FallingPlatform):
                platform.touched = False
                platform.falling = False
                platform.shake_timer = 0
                platform.fall_speed = 0
                platform.rect.y = platform.original_x  # Reset to original position

        # Reset collectibles (only non-collected ones stay)
        for collectible in self.collectibles:
            # Could optionally reset collectibles here
            pass


def load_level(level_number):
    """Load a level by number"""
    level = Level(level_number)

    # Try to load from JSON file
    filepath = os.path.join('assets', 'levels', f'level{level_number}.json')

    if os.path.exists(filepath):
        if level.load_from_json(filepath):
            return level

    # If no file or loading failed, create default level
    if level_number == 1:
        level.create_default()
        return level

    return None
