"""
Platform Classes
Handles different types of platforms: normal, moving, falling, bouncy, one-way
"""

import pygame
import math
from constants import *


class Platform:
    """Base platform class"""

    def __init__(self, x, y, width, height, platform_type='normal'):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        self.properties = PLATFORM_TYPES.get(platform_type, PLATFORM_TYPES['normal'])
        self.color = self.properties['color']
        self.friction = self.properties['friction']
        self.active = True

    def update(self):
        """Override in subclasses"""
        pass

    def draw(self, screen, camera_offset):
        """Draw the platform with camera offset"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        pygame.draw.rect(screen, self.color, draw_rect)
        # Add border for depth
        pygame.draw.rect(screen, BLACK, draw_rect, 2)

    def get_collision_rect(self):
        """Get the collision rectangle"""
        return self.rect


class MovingPlatform(Platform):
    """Platform that moves in a pattern"""

    def __init__(self, x, y, width, height, platform_type='normal',
                 pattern='horizontal', speed=2, distance=200):
        super().__init__(x, y, width, height, platform_type)
        self.start_x = x
        self.start_y = y
        self.pattern = pattern
        self.speed = speed
        self.distance = distance
        self.time = 0

    def update(self):
        """Update platform position based on pattern"""
        self.time += 1

        if self.pattern == 'horizontal':
            # Move back and forth horizontally
            offset = math.sin(self.time * 0.02 * self.speed) * self.distance
            self.rect.x = self.start_x + offset

        elif self.pattern == 'vertical':
            # Move back and forth vertically
            offset = math.sin(self.time * 0.02 * self.speed) * self.distance
            self.rect.y = self.start_y + offset

        elif self.pattern == 'circular':
            # Move in a circle
            angle = self.time * 0.02 * self.speed
            self.rect.x = self.start_x + math.cos(angle) * self.distance
            self.rect.y = self.start_y + math.sin(angle) * self.distance

        elif self.pattern == 'square':
            # Move in a square pattern
            cycle = (self.time * self.speed) % (self.distance * 4)
            if cycle < self.distance:
                self.rect.x = self.start_x + cycle
                self.rect.y = self.start_y
            elif cycle < self.distance * 2:
                self.rect.x = self.start_x + self.distance
                self.rect.y = self.start_y + (cycle - self.distance)
            elif cycle < self.distance * 3:
                self.rect.x = self.start_x + self.distance - (cycle - self.distance * 2)
                self.rect.y = self.start_y + self.distance
            else:
                self.rect.x = self.start_x
                self.rect.y = self.start_y + self.distance - (cycle - self.distance * 3)

    def get_velocity(self):
        """Return the platform's current velocity for player movement"""
        old_x = self.rect.x
        old_y = self.rect.y
        self.time += 1
        self.update()
        self.time -= 1
        vel_x = self.rect.x - old_x
        vel_y = self.rect.y - old_y
        return (vel_x, vel_y)


class FallingPlatform(Platform):
    """Platform that falls after player steps on it"""

    def __init__(self, x, y, width, height, platform_type='fall'):
        super().__init__(x, y, width, height, platform_type)
        self.fall_delay = PLATFORM_TYPES['fall'].get('fall_delay', 20)
        self.touched = False
        self.shake_timer = 0
        self.fall_timer = 0
        self.falling = False
        self.fall_speed = 0
        self.original_x = x

    def trigger(self):
        """Called when player lands on platform"""
        if not self.touched and not self.falling:
            self.touched = True
            self.shake_timer = self.fall_delay

    def update(self):
        """Update falling behavior"""
        if self.shake_timer > 0:
            self.shake_timer -= 1
            # Shake effect
            if self.shake_timer % 4 < 2:
                self.rect.x = self.original_x + 2
            else:
                self.rect.x = self.original_x - 2

            if self.shake_timer == 0:
                self.falling = True
                self.rect.x = self.original_x

        if self.falling:
            self.fall_speed += GRAVITY
            self.rect.y += self.fall_speed

            # Deactivate if fallen off screen
            if self.rect.y > SCREEN_HEIGHT + 100:
                self.active = False

    def draw(self, screen, camera_offset):
        """Draw with transparency when shaking"""
        if not self.active:
            return

        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        if self.shake_timer > 0:
            # Create semi-transparent surface when shaking
            surface = pygame.Surface((self.rect.width, self.rect.height))
            surface.set_alpha(200 - (self.fall_delay - self.shake_timer) * 5)
            surface.fill(self.color)
            screen.blit(surface, draw_rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, draw_rect)

        pygame.draw.rect(screen, BLACK, draw_rect, 2)


class BouncyPlatform(Platform):
    """Platform that bounces the player high"""

    def __init__(self, x, y, width, height, platform_type='bouncy'):
        super().__init__(x, y, width, height, platform_type)
        self.bounce_strength = PLATFORM_TYPES['bouncy'].get('bounce_strength', -20)
        self.bounce_animation = 0
        self.compressed_height = height

    def trigger_bounce(self):
        """Trigger bounce animation"""
        self.bounce_animation = 10

    def update(self):
        """Update bounce animation"""
        if self.bounce_animation > 0:
            self.bounce_animation -= 1
            # Compress platform visually
            compress_factor = self.bounce_animation / 10.0
            self.compressed_height = self.rect.height * (1 - compress_factor * 0.3)

    def draw(self, screen, camera_offset):
        """Draw with bounce animation"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        # Adjust height for compression
        height_diff = self.rect.height - self.compressed_height
        draw_rect.y += height_diff
        draw_rect.height = self.compressed_height

        pygame.draw.rect(screen, self.color, draw_rect)
        pygame.draw.rect(screen, BLACK, draw_rect, 2)

        # Draw spring coils
        coil_y = draw_rect.bottom - 10
        for i in range(3):
            pygame.draw.circle(screen, BLACK,
                             (draw_rect.centerx - 10 + i * 10, int(coil_y)), 3)


class OneWayPlatform(Platform):
    """Platform you can jump through from below"""

    def __init__(self, x, y, width, height, platform_type='oneway'):
        super().__init__(x, y, width, height, platform_type)

    def draw(self, screen, camera_offset):
        """Draw with dashed pattern to indicate one-way"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        # Draw dashed pattern
        dash_width = 20
        for i in range(0, self.rect.width, dash_width * 2):
            dash_rect = pygame.Rect(draw_rect.x + i, draw_rect.y,
                                   min(dash_width, draw_rect.width - i),
                                   draw_rect.height)
            pygame.draw.rect(screen, self.color, dash_rect)
            pygame.draw.rect(screen, BLACK, dash_rect, 2)


class Hazard:
    """Deadly hazards like spikes and lava"""

    def __init__(self, x, y, width, height, hazard_type='spike'):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = hazard_type

    def draw(self, screen, camera_offset):
        """Draw hazard"""
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        if self.type == 'spike':
            # Draw triangular spikes
            num_spikes = self.rect.width // SPIKE_WIDTH
            for i in range(num_spikes):
                spike_x = draw_rect.x + i * SPIKE_WIDTH
                points = [
                    (spike_x, draw_rect.bottom),
                    (spike_x + SPIKE_WIDTH // 2, draw_rect.top),
                    (spike_x + SPIKE_WIDTH, draw_rect.bottom)
                ]
                pygame.draw.polygon(screen, SPIKE_COLOR, points)
                pygame.draw.polygon(screen, BLACK, points, 2)

        elif self.type == 'lava':
            # Draw animated lava
            pygame.draw.rect(screen, LAVA_COLOR, draw_rect)
            # Add bubbles effect (simplified)
            for i in range(0, self.rect.width, 30):
                pygame.draw.circle(screen, ORANGE,
                                 (draw_rect.x + i + 15, draw_rect.centery), 5)

    def update(self):
        """Update hazard (for animations)"""
        pass


class Collectible:
    """Coins and power-ups"""

    def __init__(self, x, y, collectible_type='coin'):
        self.type = collectible_type
        self.collected = False
        self.animation_timer = 0

        if collectible_type == 'coin':
            self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
            self.color = COIN_COLOR
            self.value = COIN_VALUE
        else:
            self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
            self.color = GREEN
            self.value = 0

    def update(self):
        """Update animation"""
        self.animation_timer += 1

    def draw(self, screen, camera_offset):
        """Draw collectible with animation"""
        if self.collected:
            return

        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        # Bobbing animation
        bob_offset = math.sin(self.animation_timer * 0.1) * 5
        draw_rect.y += bob_offset

        if self.type == 'coin':
            # Draw spinning coin
            width = abs(math.cos(self.animation_timer * 0.05)) * COIN_SIZE
            coin_rect = pygame.Rect(draw_rect.centerx - width // 2,
                                   draw_rect.y, width, COIN_SIZE)
            pygame.draw.ellipse(screen, self.color, coin_rect)
            pygame.draw.ellipse(screen, BLACK, coin_rect, 2)
        else:
            # Draw power-up
            pygame.draw.rect(screen, self.color, draw_rect)
            pygame.draw.rect(screen, BLACK, draw_rect, 2)
            # Draw "P" symbol
            font = pygame.font.Font(None, 20)
            text = font.render('P', True, BLACK)
            screen.blit(text, (draw_rect.centerx - 5, draw_rect.centery - 8))

    def collect(self):
        """Mark as collected"""
        self.collected = True
