"""
Game Constants and Configuration
All game settings, physics values, and constants are defined here.
"""

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
WINDOW_TITLE = "Platformer Adventure"

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (200, 0, 255)
CYAN = (0, 255, 255)
DARK_GRAY = (40, 40, 40)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

# Sky colors for parallax background
SKY_TOP = (135, 206, 235)
SKY_BOTTOM = (180, 220, 255)

# Physics constants
GRAVITY = 0.8
TERMINAL_VELOCITY = 20
FRICTION = 0.85

# Player constants
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 48
PLAYER_ACCELERATION = 0.8
PLAYER_MAX_SPEED = 6
PLAYER_JUMP_STRENGTH = -16
PLAYER_DOUBLE_JUMP_STRENGTH = -14
PLAYER_DASH_SPEED = 15
PLAYER_DASH_DURATION = 12  # frames
PLAYER_DASH_COOLDOWN = 40  # frames
PLAYER_WALL_SLIDE_SPEED = 2
PLAYER_WALL_JUMP_X = 10
PLAYER_WALL_JUMP_Y = -14
PLAYER_COYOTE_TIME = 6  # frames
PLAYER_JUMP_BUFFER = 8  # frames
PLAYER_MAX_HEALTH = 3
PLAYER_INVINCIBILITY_FRAMES = 90
PLAYER_COLOR = BLUE

# Squash and stretch values
SQUASH_LAND = 0.7  # Compress vertically on landing
STRETCH_JUMP = 1.3  # Stretch vertically on jump
SQUASH_RECOVERY_SPEED = 0.15  # How fast to return to normal

# Platform types
PLATFORM_TYPES = {
    'normal': {'color': GRAY, 'friction': 1.0},
    'ice': {'color': CYAN, 'friction': 0.4},
    'sticky': {'color': ORANGE, 'friction': 1.5},
    'bouncy': {'color': PURPLE, 'friction': 1.0, 'bounce_strength': -20},
    'fall': {'color': LIGHT_GRAY, 'friction': 1.0, 'fall_delay': 20},
    'oneway': {'color': YELLOW, 'friction': 1.0}  # Can jump through from below
}

# Enemy constants
ENEMY_PATROL_SPEED = 2
ENEMY_CHASE_SPEED = 4
ENEMY_CHASE_RANGE = 300
ENEMY_FLYING_AMPLITUDE = 50
ENEMY_FLYING_SPEED = 0.05
ENEMY_SHOOT_COOLDOWN = 90  # frames
ENEMY_PROJECTILE_SPEED = 7
ENEMY_KNOCKBACK = 8

# Enemy types
ENEMY_TYPES = {
    'patrol': {'color': RED, 'width': 32, 'height': 32},
    'flying': {'color': PURPLE, 'width': 36, 'height': 28},
    'shooter': {'color': ORANGE, 'width': 32, 'height': 32}
}

# Particle constants
PARTICLE_LIFETIME = 30  # frames
PARTICLE_GRAVITY = 0.3
PARTICLE_FRICTION = 0.95

# Collectible constants
COIN_SIZE = 16
COIN_VALUE = 10
COIN_COLOR = YELLOW
POWERUP_SIZE = 24
POWERUP_DURATION = 300  # frames (5 seconds)

# Hazard constants
SPIKE_WIDTH = 32
SPIKE_HEIGHT = 24
SPIKE_COLOR = RED
LAVA_COLOR = ORANGE

# Camera constants
CAMERA_LERP_SPEED = 0.1
CAMERA_LEAD_DISTANCE = 100  # pixels ahead of player in facing direction
CAMERA_SHAKE_DECAY = 0.9

# UI constants
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 20
HUD_PADDING = 20
HEART_SIZE = 30

# Game state constants
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_GAME_OVER = 'game_over'
STATE_VICTORY = 'victory'
STATE_LEVEL_TRANSITION = 'level_transition'

# Input key mappings (can be customized later)
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_JUMP = 'jump'
KEY_DASH = 'dash'
KEY_PAUSE = 'pause'

# Level constants
LEVEL_TRANSITION_DURATION = 60  # frames
