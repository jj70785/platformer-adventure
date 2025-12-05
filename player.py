"""
Player Character Class
Handles all player movement, physics, abilities, and state
"""

import pygame
from constants import *


class Player:
    """The player character with advanced movement and abilities"""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0

        # Movement state
        self.on_ground = False
        self.on_wall = 0  # -1 for left wall, 1 for right wall, 0 for none
        self.facing = 1  # 1 for right, -1 for left

        # Jump mechanics
        self.can_jump = True
        self.double_jump_available = True
        self.jump_held = False
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

        # Dash mechanics
        self.dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.dash_direction = 0

        # Wall mechanics
        self.wall_sliding = False
        self.wall_jump_timer = 0

        # Visual effects
        self.squash_stretch = 1.0  # Vertical scale
        self.landed_this_frame = False
        self.jumped_this_frame = False

        # Health and damage
        self.health = PLAYER_MAX_HEALTH
        self.invincible = False
        self.invincibility_timer = 0
        self.damaged_this_frame = False

        # Collectibles
        self.coins = 0
        self.score = 0

        # Power-ups
        self.powered_up = False
        self.powerup_timer = 0

        # Platform tracking
        self.current_platform = None
        self.last_ground_y = y

    def handle_input(self, keys):
        """Process player input"""
        if self.dashing:
            return  # No control during dash

        # Horizontal movement
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= PLAYER_ACCELERATION
            self.facing = -1
            moving = True

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += PLAYER_ACCELERATION
            self.facing = 1
            moving = True

        # Apply friction when not moving
        if not moving:
            self.vel_x *= FRICTION

        # Clamp horizontal speed
        self.vel_x = max(-PLAYER_MAX_SPEED, min(PLAYER_MAX_SPEED, self.vel_x))

        # Jump input
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]

        if jump_pressed:
            if not self.jump_held:
                self.jump_buffer_timer = PLAYER_JUMP_BUFFER
                self.attempt_jump()
            self.jump_held = True
        else:
            self.jump_held = False
            # Variable jump height - cut upward velocity if jump released early
            if self.vel_y < 0:
                self.vel_y *= 0.5

        # Dash input
        dash_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        if dash_pressed and self.dash_cooldown_timer == 0 and not self.dashing:
            self.start_dash()

    def attempt_jump(self):
        """Attempt to jump (handles ground jump, double jump, wall jump)"""
        # Wall jump
        if self.on_wall != 0 and not self.on_ground:
            self.vel_y = PLAYER_WALL_JUMP_Y
            self.vel_x = self.on_wall * -PLAYER_WALL_JUMP_X  # Jump away from wall
            self.double_jump_available = True  # Reset double jump
            self.wall_jump_timer = 5  # Brief period where player can't grab wall
            self.jumped_this_frame = True
            return

        # Ground jump or coyote time jump
        if self.on_ground or self.coyote_timer > 0:
            self.vel_y = PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.coyote_timer = 0
            self.jumped_this_frame = True
            return

        # Double jump
        if self.double_jump_available:
            self.vel_y = PLAYER_DOUBLE_JUMP_STRENGTH
            self.double_jump_available = False
            self.jumped_this_frame = True
            return

    def start_dash(self):
        """Start dash ability"""
        self.dashing = True
        self.dash_timer = PLAYER_DASH_DURATION
        self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
        self.dash_direction = self.facing
        self.vel_y = 0  # Stop vertical movement during dash
        self.invincible = True  # Brief invincibility during dash

    def update(self, platforms, hazards, collectibles):
        """Update player physics and state"""
        self.landed_this_frame = False
        self.jumped_this_frame = False
        self.damaged_this_frame = False

        # Update timers
        if self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1
        if self.wall_jump_timer > 0:
            self.wall_jump_timer -= 1
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
            if self.invincibility_timer == 0:
                self.invincible = False
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer == 0:
                self.powered_up = False

        # Dash logic
        if self.dashing:
            self.dash_timer -= 1
            self.vel_x = self.dash_direction * PLAYER_DASH_SPEED
            self.vel_y = 0
            if self.dash_timer <= 0:
                self.dashing = False
                self.invincible = False
                self.vel_x = self.dash_direction * PLAYER_MAX_SPEED

        # Apply gravity
        if not self.dashing:
            self.vel_y += GRAVITY

            # Wall sliding
            if self.on_wall != 0 and not self.on_ground and self.vel_y > 0:
                if self.wall_jump_timer == 0:
                    self.wall_sliding = True
                    self.vel_y = min(self.vel_y, PLAYER_WALL_SLIDE_SPEED)
            else:
                self.wall_sliding = False

            # Terminal velocity
            self.vel_y = min(self.vel_y, TERMINAL_VELOCITY)

        # Store previous position
        prev_on_ground = self.on_ground
        prev_y = self.rect.y

        # Move horizontally
        self.rect.x += self.vel_x
        self.handle_horizontal_collisions(platforms)

        # Move vertically
        self.rect.y += self.vel_y
        self.handle_vertical_collisions(platforms)

        # Landing detection for squash/stretch
        # Only trigger if we were actually falling (not just from gravity tick)
        if not prev_on_ground and self.on_ground and abs(prev_y - self.rect.y) > 2:
            self.landed_this_frame = True
            self.squash_stretch = SQUASH_LAND
            if abs(self.vel_y) > 5:  # Only if significant fall
                self.last_ground_y = self.rect.y

        # Jump detection for squash/stretch
        if self.jumped_this_frame:
            self.squash_stretch = STRETCH_JUMP

        # Recover squash/stretch to normal
        if self.squash_stretch < 1.0:
            self.squash_stretch += SQUASH_RECOVERY_SPEED
            if self.squash_stretch > 1.0:
                self.squash_stretch = 1.0
        elif self.squash_stretch > 1.0:
            self.squash_stretch -= SQUASH_RECOVERY_SPEED
            if self.squash_stretch < 1.0:
                self.squash_stretch = 1.0

        # Coyote time - can still jump shortly after leaving platform
        if prev_on_ground and not self.on_ground and self.vel_y >= 0:
            self.coyote_timer = PLAYER_COYOTE_TIME

        # Jump buffering - if jump pressed just before landing
        if self.on_ground and self.jump_buffer_timer > 0:
            self.attempt_jump()
            self.jump_buffer_timer = 0

        # Reset double jump when on ground or wall
        if self.on_ground or self.on_wall != 0:
            self.double_jump_available = True

        # Check hazard collisions
        self.check_hazards(hazards)

        # Check collectible collisions
        self.check_collectibles(collectibles)

        # Fall death
        if self.rect.y > SCREEN_HEIGHT + 100:
            self.take_damage(999)  # Instant death

    def handle_horizontal_collisions(self, platforms):
        """Handle collisions in the X axis"""
        self.on_wall = 0

        for platform in platforms:
            if not platform.active:
                continue

            if self.rect.colliderect(platform.rect):
                # Moving right
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.vel_x = 0
                    if not self.on_ground and self.wall_jump_timer == 0:
                        self.on_wall = 1

                # Moving left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.vel_x = 0
                    if not self.on_ground and self.wall_jump_timer == 0:
                        self.on_wall = -1

    def handle_vertical_collisions(self, platforms):
        """Handle collisions in the Y axis"""
        self.on_ground = False
        self.current_platform = None

        for platform in platforms:
            if not platform.active:
                continue

            if self.rect.colliderect(platform.rect):
                # One-way platforms - only collide from above
                if platform.type == 'oneway':
                    # Check if player is falling and was above platform
                    if self.vel_y > 0 and self.rect.bottom - self.vel_y <= platform.rect.top + 10:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.current_platform = platform
                else:
                    # Falling down (hitting top of platform)
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.current_platform = platform

                        # Apply platform friction
                        if hasattr(platform, 'friction'):
                            friction_mult = platform.friction
                            self.vel_x *= (FRICTION * friction_mult)

                        # Bouncy platform
                        if platform.type == 'bouncy':
                            self.vel_y = platform.bounce_strength
                            if hasattr(platform, 'trigger_bounce'):
                                platform.trigger_bounce()

                        # Falling platform
                        if platform.type == 'fall':
                            if hasattr(platform, 'trigger'):
                                platform.trigger()

                    # Jumping up (hitting bottom of platform)
                    elif self.vel_y < 0:
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0

        # Move with platform if on a moving platform
        if self.on_ground and self.current_platform:
            if hasattr(self.current_platform, 'get_velocity'):
                plat_vel = self.current_platform.get_velocity()
                self.rect.x += plat_vel[0]
                self.rect.y += plat_vel[1]

    def check_hazards(self, hazards):
        """Check collision with hazards"""
        if self.invincible:
            return

        for hazard in hazards:
            if self.rect.colliderect(hazard.rect):
                self.take_damage(1)
                self.damaged_this_frame = True
                break

    def check_collectibles(self, collectibles):
        """Check collision with collectibles"""
        for collectible in collectibles:
            if collectible.collected:
                continue

            if self.rect.colliderect(collectible.rect):
                if collectible.type == 'coin':
                    self.coins += 1
                    self.score += collectible.value
                elif collectible.type == 'powerup':
                    self.powered_up = True
                    self.powerup_timer = POWERUP_DURATION

                collectible.collect()

    def take_damage(self, amount):
        """Take damage"""
        if self.invincible:
            return

        self.health -= amount
        if self.health > 0:
            self.invincible = True
            self.invincibility_timer = PLAYER_INVINCIBILITY_FRAMES
        else:
            self.health = 0
            # Death handled in main game

    def heal(self, amount):
        """Heal player"""
        self.health = min(self.health + amount, PLAYER_MAX_HEALTH)

    def draw(self, screen, camera_offset):
        """Draw player with squash/stretch and invincibility flicker"""
        # Flicker when invincible
        if self.invincible and (self.invincibility_timer // 5) % 2 == 0:
            return  # Don't draw on certain frames for flicker effect

        # Calculate draw position
        draw_x = self.rect.centerx - camera_offset[0]
        draw_y = self.rect.bottom - camera_offset[1]

        # Apply squash and stretch
        width = PLAYER_WIDTH
        height = PLAYER_HEIGHT * self.squash_stretch

        # Adjust y position to keep bottom anchored
        draw_y -= height

        # Draw player rectangle
        player_rect = pygame.Rect(draw_x - width // 2, draw_y, width, height)

        # Color based on state
        color = PLAYER_COLOR
        if self.powered_up:
            color = YELLOW
        if self.dashing:
            color = CYAN

        pygame.draw.rect(screen, color, player_rect)
        pygame.draw.rect(screen, BLACK, player_rect, 2)

        # Draw eyes
        eye_y = player_rect.top + height * 0.3
        eye_offset = 6
        pygame.draw.circle(screen, WHITE,
                          (int(draw_x - eye_offset), int(eye_y)), 4)
        pygame.draw.circle(screen, WHITE,
                          (int(draw_x + eye_offset), int(eye_y)), 4)
        pygame.draw.circle(screen, BLACK,
                          (int(draw_x - eye_offset + self.facing * 2), int(eye_y)), 2)
        pygame.draw.circle(screen, BLACK,
                          (int(draw_x + eye_offset + self.facing * 2), int(eye_y)), 2)

    def draw_ui(self, screen):
        """Draw player UI (health, coins, etc.)"""
        # Draw health hearts
        for i in range(PLAYER_MAX_HEALTH):
            x = HUD_PADDING + i * (HEART_SIZE + 10)
            y = HUD_PADDING

            if i < self.health:
                # Full heart
                pygame.draw.circle(screen, RED, (x + 10, y + 10), 10)
                pygame.draw.circle(screen, RED, (x + 20, y + 10), 10)
                points = [(x + 10, y + 15), (x + 30, y + 15),
                         (x + 20, y + 28)]
                pygame.draw.polygon(screen, RED, points)
            else:
                # Empty heart outline
                pygame.draw.circle(screen, GRAY, (x + 10, y + 10), 10, 2)
                pygame.draw.circle(screen, GRAY, (x + 20, y + 10), 10, 2)
                points = [(x + 10, y + 15), (x + 30, y + 15),
                         (x + 20, y + 28)]
                pygame.draw.polygon(screen, GRAY, points, 2)

        # Draw coin count
        font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        coin_text = font.render(f'Coins: {self.coins}', True, YELLOW)
        screen.blit(coin_text, (HUD_PADDING, HUD_PADDING + 50))

        # Draw score
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (HUD_PADDING, HUD_PADDING + 80))

        # Draw dash cooldown indicator
        if self.dash_cooldown_timer > 0:
            bar_width = 100
            bar_height = 10
            bar_x = HUD_PADDING
            bar_y = HUD_PADDING + 120

            # Background
            pygame.draw.rect(screen, GRAY,
                           (bar_x, bar_y, bar_width, bar_height))

            # Cooldown progress
            progress = 1 - (self.dash_cooldown_timer / PLAYER_DASH_COOLDOWN)
            pygame.draw.rect(screen, CYAN,
                           (bar_x, bar_y, bar_width * progress, bar_height))

            # Border
            pygame.draw.rect(screen, BLACK,
                           (bar_x, bar_y, bar_width, bar_height), 2)

    def is_alive(self):
        """Check if player is alive"""
        return self.health > 0

    def reset(self, x, y):
        """Reset player to checkpoint"""
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.health = PLAYER_MAX_HEALTH
        self.invincible = False
        self.invincibility_timer = 0
