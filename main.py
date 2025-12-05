"""
Platformer Adventure - Main Game File
Run this file to start the game!
"""

import pygame
import sys
from constants import *
from player import Player
from camera import Camera, ParallaxBackground
from particles import ParticleSystem
from level import load_level
from enemy import PatrolEnemy, FlyingEnemy, ShooterEnemy, ChasingEnemy


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = STATE_MENU
        self.current_level_number = 1
        self.current_level = None
        self.player = None
        self.camera = None
        self.particles = None
        self.background = None
        self.enemies = []

        # UI
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        # Transition
        self.transition_timer = 0

        # Menu selection
        self.menu_selection = 0
        self.menu_options = ['Start Game', 'Controls', 'Quit']

    def start_game(self):
        """Initialize a new game"""
        self.current_level_number = 1
        self.load_level(self.current_level_number)
        self.state = STATE_PLAYING

    def load_level(self, level_number):
        """Load a specific level"""
        self.current_level = load_level(level_number)
        if self.current_level is None:
            print(f"Could not load level {level_number}")
            self.state = STATE_MENU
            return

        # Create player at spawn point
        spawn = self.current_level.get_spawn_point()
        self.player = Player(spawn[0], spawn[1])

        # Create camera
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.set_bounds(0, self.current_level.width,
                               0, self.current_level.height)

        # Create particle system
        self.particles = ParticleSystem()

        # Create background
        self.background = ParallaxBackground()

        # Create enemies (for default level)
        self.enemies = []
        if level_number == 1:
            self.enemies.append(PatrolEnemy(600, 350, 150))
            self.enemies.append(PatrolEnemy(1200, 350, 200))
            self.enemies.append(FlyingEnemy(1500, 200, 'sine'))
            self.enemies.append(ShooterEnemy(2200, 250))
            self.enemies.append(ChasingEnemy(2800, 200))

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.select_menu_option()

                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.state = STATE_PAUSED

                elif self.state == STATE_PAUSED:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_r:
                        self.restart_level()
                    elif event.key == pygame.K_m:
                        self.state = STATE_MENU

                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.restart_level()
                    elif event.key == pygame.K_m:
                        self.state = STATE_MENU

                elif self.state == STATE_VICTORY:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.next_level()
                    elif event.key == pygame.K_m:
                        self.state = STATE_MENU

    def select_menu_option(self):
        """Handle menu selection"""
        option = self.menu_options[self.menu_selection]

        if option == 'Start Game':
            self.start_game()
        elif option == 'Controls':
            # Could add a controls screen here
            pass
        elif option == 'Quit':
            self.running = False

    def restart_level(self):
        """Restart current level"""
        self.load_level(self.current_level_number)
        self.state = STATE_PLAYING

    def next_level(self):
        """Load next level"""
        self.current_level_number += 1
        next_level = load_level(self.current_level_number)

        if next_level:
            self.load_level(self.current_level_number)
            self.state = STATE_LEVEL_TRANSITION
            self.transition_timer = LEVEL_TRANSITION_DURATION
        else:
            # No more levels - back to menu
            self.state = STATE_MENU

    def update(self):
        """Update game state"""
        if self.state == STATE_PLAYING:
            self.update_playing()
        elif self.state == STATE_LEVEL_TRANSITION:
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.state = STATE_PLAYING

    def update_playing(self):
        """Update game when playing"""
        # Get keys
        keys = pygame.key.get_pressed()

        # Update player
        self.player.handle_input(keys)
        self.player.update(
            self.current_level.get_active_platforms(),
            self.current_level.hazards,
            self.current_level.collectibles
        )

        # Create particles based on player state
        if self.player.landed_this_frame:
            self.particles.emit_dust(
                self.player.rect.centerx,
                self.player.rect.bottom,
                direction=1 if self.player.vel_x > 0 else -1,
                count=10
            )
            # Screen shake on landing from height
            if abs(self.player.vel_y) > 10:
                self.camera.add_shake(5)

        if self.player.jumped_this_frame:
            self.particles.emit_jump(
                self.player.rect.centerx,
                self.player.rect.bottom
            )

        if self.player.dashing:
            self.particles.emit_dash_trail(
                self.player.rect.centerx,
                self.player.rect.centery,
                CYAN
            )

        if self.player.wall_sliding:
            self.particles.emit_wall_slide(
                self.player.rect.right if self.player.on_wall > 0 else self.player.rect.left,
                self.player.rect.centery,
                self.player.on_wall
            )

        if self.player.on_ground and abs(self.player.vel_x) > 2:
            self.particles.emit_running(
                self.player.rect.centerx,
                self.player.rect.bottom,
                self.player.facing
            )

        if self.player.damaged_this_frame:
            self.particles.emit_damage(
                self.player.rect.centerx,
                self.player.rect.centery
            )
            self.camera.add_shake(8)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player, self.current_level.get_active_platforms())

            # Check stomp
            if enemy.check_stomp(self.player):
                killed = enemy.take_damage()
                if killed:
                    self.particles.emit_explosion(
                        enemy.rect.centerx,
                        enemy.rect.centery,
                        enemy.color
                    )
                    self.player.score += 100
                    self.camera.add_shake(6)

            # Check collision damage
            elif enemy.check_collision(self.player):
                self.player.take_damage(1)

            # Check shooter projectiles
            if isinstance(enemy, ShooterEnemy):
                if enemy.check_projectile_hit(self.player):
                    self.player.take_damage(1)

        # Update collectibles and emit particles
        for collectible in self.current_level.collectibles:
            if not collectible.collected:
                prev_collected = collectible.collected
                # Collectibles are checked in player.update()
                # But we emit particles here when newly collected
                if self.player.rect.colliderect(collectible.rect) and not prev_collected:
                    self.particles.emit_collect(
                        collectible.rect.centerx,
                        collectible.rect.centery,
                        collectible.color
                    )

        # Update level
        self.current_level.update(self.player)

        # Update particles
        self.particles.update()

        # Update camera
        self.camera.update(
            self.player.rect.centerx,
            self.player.rect.centery,
            self.player.facing
        )

        # Check win condition
        if self.current_level.completed:
            self.state = STATE_VICTORY

        # Check death
        if not self.player.is_alive():
            self.state = STATE_GAME_OVER

    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)

        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING or self.state == STATE_PAUSED:
            self.draw_playing()
            if self.state == STATE_PAUSED:
                self.draw_pause_overlay()
        elif self.state == STATE_GAME_OVER:
            self.draw_playing()  # Show game state
            self.draw_game_over()
        elif self.state == STATE_VICTORY:
            self.draw_playing()  # Show game state
            self.draw_victory()
        elif self.state == STATE_LEVEL_TRANSITION:
            self.draw_level_transition()

        pygame.display.flip()

    def draw_menu(self):
        """Draw main menu"""
        # Title
        title = self.font_large.render('PLATFORMER ADVENTURE', True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Menu options
        for i, option in enumerate(self.menu_options):
            color = YELLOW if i == self.menu_selection else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
            self.screen.blit(text, text_rect)

            # Draw arrow next to selected
            if i == self.menu_selection:
                arrow = self.font_medium.render('>', True, YELLOW)
                self.screen.blit(arrow, (text_rect.left - 40, text_rect.top))

        # Controls hint
        controls_text = [
            'Arrow Keys / WASD - Move',
            'Space - Jump (press twice for double jump)',
            'Shift / X - Dash',
            'ESC / P - Pause'
        ]
        y = 500
        for line in controls_text:
            text = self.font_small.render(line, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30

    def draw_playing(self):
        """Draw game while playing"""
        camera_offset = self.camera.get_offset()

        # Draw parallax background
        self.background.draw(self.screen, camera_offset)

        # Draw level
        self.current_level.draw(self.screen, camera_offset)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, camera_offset)

        # Draw particles
        self.particles.draw(self.screen, camera_offset)

        # Draw player
        self.player.draw(self.screen, camera_offset)

        # Draw UI
        self.player.draw_ui(self.screen)

        # Draw level number
        level_text = self.font_small.render(f'Level {self.current_level_number}',
                                           True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, HUD_PADDING))

        # Draw particle count (debug)
        # particle_text = self.font_small.render(f'Particles: {self.particles.get_count()}',
        #                                        True, WHITE)
        # self.screen.blit(particle_text, (SCREEN_WIDTH - 200, HUD_PADDING + 30))

    def draw_pause_overlay(self):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self.font_large.render('PAUSED', True, CYAN)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(pause_text, pause_rect)

        # Options
        options = [
            'ESC / P - Resume',
            'R - Restart Level',
            'M - Main Menu'
        ]
        y = 350
        for option in options:
            text = self.font_medium.render(option, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 50

    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font_large.render('GAME OVER', True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(game_over_text, game_over_rect)

        # Score
        score_text = self.font_medium.render(f'Score: {self.player.score}', True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)

        # Options
        retry_text = self.font_medium.render('R - Retry', True, WHITE)
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(retry_text, retry_rect)

        menu_text = self.font_medium.render('M - Main Menu', True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(menu_text, menu_rect)

    def draw_victory(self):
        """Draw victory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Victory text
        victory_text = self.font_large.render('LEVEL COMPLETE!', True, GREEN)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(victory_text, victory_rect)

        # Stats
        stats = [
            f'Score: {self.player.score}',
            f'Coins: {self.player.coins}',
            f'Health: {self.player.health}/{PLAYER_MAX_HEALTH}'
        ]
        y = 300
        for stat in stats:
            text = self.font_medium.render(stat, True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 50

        # Continue prompt
        continue_text = self.font_medium.render('Press SPACE to continue', True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(continue_text, continue_rect)

        menu_text = self.font_small.render('M - Main Menu', True, LIGHT_GRAY)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(menu_text, menu_rect)

    def draw_level_transition(self):
        """Draw level transition screen"""
        self.screen.fill(BLACK)

        # Fade effect based on timer
        alpha = 255
        if self.transition_timer > LEVEL_TRANSITION_DURATION // 2:
            # Fade in
            alpha = int(255 * (1 - (self.transition_timer - LEVEL_TRANSITION_DURATION // 2) /
                              (LEVEL_TRANSITION_DURATION // 2)))
        else:
            # Fade out
            alpha = int(255 * (self.transition_timer / (LEVEL_TRANSITION_DURATION // 2)))

        text = self.font_large.render(f'Level {self.current_level_number}', True, CYAN)
        text.set_alpha(alpha)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
