"""
Particle Effects System
Handles all visual particle effects: dust, trails, explosions, etc.
"""

import pygame
import random
import math
from constants import *


class Particle:
    """Individual particle"""

    def __init__(self, x, y, color, vel_x=0, vel_y=0, lifetime=PARTICLE_LIFETIME,
                 size=4, gravity=True, fade=True):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.size = size
        self.use_gravity = gravity
        self.fade = fade
        self.alpha = 255

    def update(self):
        """Update particle physics"""
        self.x += self.vel_x
        self.y += self.vel_y

        if self.use_gravity:
            self.vel_y += PARTICLE_GRAVITY

        self.vel_x *= PARTICLE_FRICTION
        self.vel_y *= PARTICLE_FRICTION

        self.lifetime -= 1

        if self.fade:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))

    def draw(self, screen, camera_offset):
        """Draw particle"""
        if self.lifetime <= 0:
            return

        draw_x = int(self.x - camera_offset[0])
        draw_y = int(self.y - camera_offset[1])

        # Create surface with alpha for fading
        if self.fade and self.alpha < 255:
            surface = pygame.Surface((self.size * 2, self.size * 2))
            surface.set_alpha(self.alpha)
            surface.fill(BLACK)
            surface.set_colorkey(BLACK)
            pygame.draw.circle(surface, self.color, (self.size, self.size), self.size)
            screen.blit(surface, (draw_x - self.size, draw_y - self.size))
        else:
            pygame.draw.circle(screen, self.color, (draw_x, draw_y), self.size)

    def is_dead(self):
        """Check if particle should be removed"""
        return self.lifetime <= 0


class ParticleSystem:
    """Manages all particles in the game"""

    def __init__(self):
        self.particles = []

    def add_particle(self, particle):
        """Add a single particle"""
        self.particles.append(particle)

    def emit_dust(self, x, y, direction=0, count=8):
        """Emit dust cloud particles (for landing)"""
        for _ in range(count):
            vel_x = random.uniform(-3, 3) + direction * 2
            vel_y = random.uniform(-2, -5)
            size = random.randint(2, 5)
            color = random.choice([LIGHT_GRAY, GRAY, WHITE])
            particle = Particle(x, y, color, vel_x, vel_y,
                              lifetime=random.randint(15, 30),
                              size=size, gravity=True, fade=True)
            self.particles.append(particle)

    def emit_jump(self, x, y, count=5):
        """Emit particles when jumping"""
        for _ in range(count):
            vel_x = random.uniform(-2, 2)
            vel_y = random.uniform(0, 2)
            size = random.randint(2, 4)
            particle = Particle(x, y, WHITE, vel_x, vel_y,
                              lifetime=random.randint(10, 20),
                              size=size, gravity=True, fade=True)
            self.particles.append(particle)

    def emit_dash_trail(self, x, y, color=CYAN):
        """Emit trail particles during dash"""
        for _ in range(3):
            vel_x = random.uniform(-1, 1)
            vel_y = random.uniform(-1, 1)
            size = random.randint(3, 6)
            particle = Particle(x, y, color, vel_x, vel_y,
                              lifetime=random.randint(15, 25),
                              size=size, gravity=False, fade=True)
            self.particles.append(particle)

    def emit_running(self, x, y, direction):
        """Emit small particles while running"""
        if random.random() < 0.3:  # Don't emit every frame
            vel_x = random.uniform(-1, 1) - direction * 2
            vel_y = random.uniform(-1, 0)
            particle = Particle(x, y, LIGHT_GRAY, vel_x, vel_y,
                              lifetime=random.randint(5, 15),
                              size=2, gravity=False, fade=True)
            self.particles.append(particle)

    def emit_wall_slide(self, x, y, side):
        """Emit particles when wall sliding"""
        if random.random() < 0.5:
            vel_x = side * random.uniform(1, 3)
            vel_y = random.uniform(-1, 2)
            particle = Particle(x, y, LIGHT_GRAY, vel_x, vel_y,
                              lifetime=random.randint(10, 20),
                              size=3, gravity=True, fade=True)
            self.particles.append(particle)

    def emit_explosion(self, x, y, color=ORANGE, count=20):
        """Emit explosion particles (for enemy death, etc.)"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            size = random.randint(3, 7)
            particle = Particle(x, y, color, vel_x, vel_y,
                              lifetime=random.randint(20, 40),
                              size=size, gravity=True, fade=True)
            self.particles.append(particle)

    def emit_collect(self, x, y, color=YELLOW, count=12):
        """Emit particles when collecting items"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - 2  # Slight upward bias
            size = random.randint(2, 5)
            particle = Particle(x, y, color, vel_x, vel_y,
                              lifetime=random.randint(15, 30),
                              size=size, gravity=True, fade=True)
            self.particles.append(particle)

    def emit_damage(self, x, y, count=15):
        """Emit red particles when player takes damage"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            size = random.randint(3, 6)
            particle = Particle(x, y, RED, vel_x, vel_y,
                              lifetime=random.randint(15, 25),
                              size=size, gravity=True, fade=True)
            self.particles.append(particle)

    def emit_sparkle(self, x, y, color=YELLOW):
        """Emit single sparkle particle (for coins, etc.)"""
        particle = Particle(x, y, color,
                          vel_x=random.uniform(-1, 1),
                          vel_y=random.uniform(-2, -4),
                          lifetime=20, size=3, gravity=True, fade=True)
        self.particles.append(particle)

    def update(self):
        """Update all particles and remove dead ones"""
        for particle in self.particles[:]:  # Create copy to safely remove
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)

    def draw(self, screen, camera_offset):
        """Draw all active particles"""
        for particle in self.particles:
            particle.draw(screen, camera_offset)

    def clear(self):
        """Remove all particles"""
        self.particles.clear()

    def get_count(self):
        """Get current particle count"""
        return len(self.particles)
