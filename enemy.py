"""
Enemy Classes
Different enemy types with AI behaviors
"""

import pygame
import math
import random
from constants import *


class Enemy:
    """Base enemy class"""

    def __init__(self, x, y, enemy_type='patrol'):
        self.type = enemy_type
        self.properties = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES['patrol'])
        self.rect = pygame.Rect(x, y, self.properties['width'], self.properties['height'])
        self.color = self.properties['color']
        self.alive = True
        self.health = 1
        self.stunned = False
        self.stun_timer = 0

    def update(self, player, platforms):
        """Override in subclasses"""
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0:
                self.stunned = False

    def draw(self, screen, camera_offset):
        """Draw enemy"""
        if not self.alive:
            return

        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        # Flicker when stunned
        if self.stunned and (self.stun_timer // 5) % 2 == 0:
            color = LIGHT_GRAY
        else:
            color = self.color

        pygame.draw.rect(screen, color, draw_rect)
        pygame.draw.rect(screen, BLACK, draw_rect, 2)

        # Draw eyes
        eye_y = draw_rect.centery - 5
        pygame.draw.circle(screen, WHITE, (draw_rect.centerx - 8, eye_y), 4)
        pygame.draw.circle(screen, WHITE, (draw_rect.centerx + 8, eye_y), 4)
        pygame.draw.circle(screen, BLACK, (draw_rect.centerx - 8, eye_y), 2)
        pygame.draw.circle(screen, BLACK, (draw_rect.centerx + 8, eye_y), 2)

    def take_damage(self, amount=1):
        """Take damage"""
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True  # Return True if killed
        else:
            self.stunned = True
            self.stun_timer = 20
            return False

    def check_stomp(self, player):
        """Check if player stomped on this enemy"""
        if not self.alive or self.stunned:
            return False

        # Check if player is falling and hitting from above
        if player.vel_y > 0 and player.rect.bottom <= self.rect.top + 20:
            if player.rect.colliderect(self.rect):
                # Player bounces
                player.vel_y = -12
                return True

        return False

    def check_collision(self, player):
        """Check if enemy collides with player (damage)"""
        if not self.alive or self.stunned:
            return False

        if player.rect.colliderect(self.rect):
            # Don't damage if player is dashing (invincible)
            if not player.dashing:
                return True

        return False


class PatrolEnemy(Enemy):
    """Enemy that patrols back and forth"""

    def __init__(self, x, y, patrol_distance=200):
        super().__init__(x, y, 'patrol')
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.direction = 1
        self.vel_x = ENEMY_PATROL_SPEED
        self.vel_y = 0
        self.on_ground = False

    def update(self, player, platforms):
        """Update patrol behavior"""
        super().update(player, platforms)

        if not self.alive or self.stunned:
            return

        # Apply gravity
        self.vel_y += GRAVITY
        self.vel_y = min(self.vel_y, TERMINAL_VELOCITY)

        # Move
        self.rect.x += self.vel_x * self.direction
        self.rect.y += self.vel_y

        # Check platform collisions
        self.on_ground = False
        for platform in platforms:
            if not platform.active:
                continue

            if self.rect.colliderect(platform.rect):
                # Landing on platform
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

        # Turn around at patrol limits
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.direction *= -1

        # Turn around at edges
        if self.on_ground:
            # Check if there's ground ahead
            check_rect = pygame.Rect(
                self.rect.x + (self.rect.width * self.direction),
                self.rect.bottom,
                10, 10
            )
            has_ground = False
            for platform in platforms:
                if platform.active and check_rect.colliderect(platform.rect):
                    has_ground = True
                    break

            if not has_ground:
                self.direction *= -1


class FlyingEnemy(Enemy):
    """Enemy that flies in a pattern"""

    def __init__(self, x, y, pattern='sine'):
        super().__init__(x, y, 'flying')
        self.start_x = x
        self.start_y = y
        self.pattern = pattern
        self.time = random.random() * 100  # Random start time

    def update(self, player, platforms):
        """Update flying pattern"""
        super().update(player, platforms)

        if not self.alive or self.stunned:
            return

        self.time += 1

        if self.pattern == 'sine':
            # Sine wave pattern
            self.rect.x = self.start_x + math.cos(self.time * 0.03) * 150
            self.rect.y = self.start_y + math.sin(self.time * 0.05) * ENEMY_FLYING_AMPLITUDE

        elif self.pattern == 'circle':
            # Circular pattern
            angle = self.time * 0.03
            radius = 100
            self.rect.x = self.start_x + math.cos(angle) * radius
            self.rect.y = self.start_y + math.sin(angle) * radius

        elif self.pattern == 'vertical':
            # Up and down
            self.rect.y = self.start_y + math.sin(self.time * 0.05) * ENEMY_FLYING_AMPLITUDE

    def draw(self, screen, camera_offset):
        """Draw flying enemy with wings"""
        super().draw(screen, camera_offset)

        if not self.alive:
            return

        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        # Draw wings
        wing_offset = abs(math.sin(self.time * 0.2)) * 8
        # Left wing
        pygame.draw.line(screen, self.color,
                        (draw_rect.left, draw_rect.centery),
                        (draw_rect.left - 15, draw_rect.centery - wing_offset), 3)
        # Right wing
        pygame.draw.line(screen, self.color,
                        (draw_rect.right, draw_rect.centery),
                        (draw_rect.right + 15, draw_rect.centery - wing_offset), 3)


class ShooterEnemy(Enemy):
    """Enemy that shoots projectiles at the player"""

    def __init__(self, x, y):
        super().__init__(x, y, 'shooter')
        self.shoot_cooldown = 0
        self.projectiles = []
        self.detection_range = ENEMY_CHASE_RANGE

    def update(self, player, platforms):
        """Update shooter behavior"""
        super().update(player, platforms)

        if not self.alive or self.stunned:
            return

        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Check if player is in range
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)

        if distance < self.detection_range and self.shoot_cooldown == 0:
            # Shoot at player
            self.shoot(player)
            self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_expired():
                self.projectiles.remove(projectile)

    def shoot(self, player):
        """Shoot projectile at player"""
        # Calculate direction to player
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)

        if distance > 0:
            vel_x = (dist_x / distance) * ENEMY_PROJECTILE_SPEED
            vel_y = (dist_y / distance) * ENEMY_PROJECTILE_SPEED

            projectile = Projectile(self.rect.centerx, self.rect.centery,
                                   vel_x, vel_y)
            self.projectiles.append(projectile)

    def draw(self, screen, camera_offset):
        """Draw shooter enemy and projectiles"""
        super().draw(screen, camera_offset)

        # Draw gun barrel
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset[0]
        draw_rect.y -= camera_offset[1]

        pygame.draw.rect(screen, BLACK,
                        (draw_rect.right, draw_rect.centery - 3, 10, 6))

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, camera_offset)

    def check_projectile_hit(self, player):
        """Check if any projectile hit the player"""
        for projectile in self.projectiles[:]:
            if projectile.check_collision(player):
                self.projectiles.remove(projectile)
                return True
        return False


class Projectile:
    """Projectile shot by shooter enemies"""

    def __init__(self, x, y, vel_x, vel_y):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = 6
        self.lifetime = 120  # 2 seconds at 60 fps
        self.color = ORANGE

    def update(self):
        """Update projectile position"""
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1

    def draw(self, screen, camera_offset):
        """Draw projectile"""
        draw_x = int(self.x - camera_offset[0])
        draw_y = int(self.y - camera_offset[1])

        pygame.draw.circle(screen, self.color, (draw_x, draw_y), self.radius)
        pygame.draw.circle(screen, BLACK, (draw_x, draw_y), self.radius, 2)

    def check_collision(self, player):
        """Check collision with player"""
        if player.invincible or player.dashing:
            return False

        dist_x = self.x - player.rect.centerx
        dist_y = self.y - player.rect.centery
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)

        return distance < self.radius + (PLAYER_WIDTH / 2)

    def is_expired(self):
        """Check if projectile should be removed"""
        return self.lifetime <= 0


class ChasingEnemy(Enemy):
    """Enemy that chases the player when in range"""

    def __init__(self, x, y):
        super().__init__(x, y, 'patrol')
        self.start_x = x
        self.start_y = y
        self.vel_x = 0
        self.vel_y = 0
        self.chasing = False
        self.chase_range = ENEMY_CHASE_RANGE
        self.return_speed = 2

    def update(self, player, platforms):
        """Update chasing behavior"""
        super().update(player, platforms)

        if not self.alive or self.stunned:
            return

        # Check distance to player
        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)

        if distance < self.chase_range:
            # Chase player
            self.chasing = True
            if distance > 0:
                self.vel_x = (dist_x / distance) * ENEMY_CHASE_SPEED
                self.vel_y = (dist_y / distance) * ENEMY_CHASE_SPEED
        else:
            # Return to start position
            self.chasing = False
            dist_to_start_x = self.start_x - self.rect.x
            dist_to_start_y = self.start_y - self.rect.y
            dist_to_start = math.sqrt(dist_to_start_x ** 2 + dist_to_start_y ** 2)

            if dist_to_start > 5:
                self.vel_x = (dist_to_start_x / dist_to_start) * self.return_speed
                self.vel_y = (dist_to_start_y / dist_to_start) * self.return_speed
            else:
                self.vel_x = 0
                self.vel_y = 0

        # Move
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self, screen, camera_offset):
        """Draw chasing enemy"""
        super().draw(screen, camera_offset)

        # Draw exclamation mark when chasing
        if self.chasing and self.alive:
            draw_x = self.rect.centerx - camera_offset[0]
            draw_y = self.rect.top - camera_offset[1] - 20

            font = pygame.font.Font(None, 30)
            text = font.render('!', True, RED)
            screen.blit(text, (draw_x - 5, draw_y))
