# Platformer Adventure

A feature-rich 2D platformer game built with Python and Pygame, featuring advanced physics, smooth movement, visual effects, and engaging gameplay!

## Features

### Movement & Physics
- **Responsive Controls**: Smooth acceleration and deceleration
- **Variable Jump Height**: Hold jump longer to jump higher
- **Double Jump**: Jump a second time in mid-air
- **Dash Ability**: Quick dash with cooldown system
- **Wall Sliding**: Slow your fall when touching walls
- **Wall Jump**: Jump off walls to reach new heights
- **Coyote Time**: Grace period to jump after leaving a platform
- **Jump Buffering**: Press jump slightly before landing for instant jump
- **Squash & Stretch**: Character deforms on landing and jumping for visual feedback

### Visual Effects
- **Particle System**: Dust clouds, jump particles, dash trails, and more
- **Parallax Scrolling**: Multi-layer background for depth
- **Smooth Camera**: Camera smoothly follows player with look-ahead
- **Screen Shake**: Impact feedback on landings and damage
- **Animations**: Player eye tracking and squash/stretch effects

### Platform Varieties
- **Normal Platforms**: Standard solid platforms
- **Ice Platforms**: Slippery surfaces with reduced friction
- **Sticky Platforms**: Extra friction for precise control
- **Bouncy Platforms**: Launch you high into the air
- **Falling Platforms**: Crumble after you step on them
- **One-Way Platforms**: Jump through from below
- **Moving Platforms**: Horizontal, vertical, circular, and square patterns

### Combat & Enemies
- **Patrol Enemies**: Walk back and forth on platforms
- **Flying Enemies**: Move in patterns through the air
- **Shooter Enemies**: Fire projectiles at the player
- **Chasing Enemies**: Follow you when you get close
- **Stomp Mechanic**: Jump on enemies to defeat them
- **Health System**: 3 hearts with invincibility frames after damage
- **Score System**: Earn points for collecting coins and defeating enemies

### Level Design
- **Hazards**: Spikes and lava that damage on contact
- **Collectibles**: Coins for points and power-ups
- **Checkpoints**: Respawn at activated checkpoints
- **Goal System**: Reach the goal to complete the level
- **JSON Level Format**: Easy to create custom levels

## Controls

| Action | Keys |
|--------|------|
| Move Left | Left Arrow or A |
| Move Right | Right Arrow or D |
| Jump | Space, Up Arrow, or W |
| Double Jump | Press jump again in mid-air |
| Wall Jump | Jump while touching a wall |
| Dash | Left Shift or X |
| Pause | ESC or P |
| Restart (when dead) | R |
| Main Menu | M (from pause/game over) |

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

Run the game:
```bash
python main.py
```

### Gameplay Tips

1. **Master the Movement**: Practice wall jumping and dashing to reach difficult areas
2. **Collect Everything**: Coins increase your score
3. **Use Power-ups**: Green power-ups give you temporary invincibility
4. **Stomp Enemies**: Jump on enemies from above to defeat them safely
5. **Watch for Hazards**: Red spikes are deadly - avoid them!
6. **Find Checkpoints**: Green flags save your progress through the level
7. **Experiment with Platforms**:
   - Purple platforms bounce you high
   - Cyan platforms are slippery
   - Yellow platforms can be jumped through from below
   - Gray cracked platforms fall when you step on them

## Game Structure

```
PONG/
├── main.py              # Entry point and game loop
├── player.py            # Player character with movement
├── enemy.py             # Enemy AI and types
├── platform.py          # Platform types and hazards
├── camera.py            # Camera system and parallax background
├── particles.py         # Particle effects
├── level.py             # Level loading and management
├── constants.py         # Game settings and physics constants
├── requirements.txt     # Python dependencies
└── assets/
    ├── levels/          # Level JSON files
    ├── sprites/         # (Future: sprite images)
    ├── sounds/          # (Future: sound effects)
    └── music/           # (Future: background music)
```

## Creating Custom Levels

You can create custom levels using JSON! Create a new file in `assets/levels/` named `level<number>.json`:

```json
{
  "width": 4000,
  "height": 800,
  "spawn": [100, 100],
  "platforms": [
    {
      "x": 0,
      "y": 750,
      "width": 4000,
      "height": 50,
      "type": "normal"
    },
    {
      "x": 500,
      "y": 600,
      "width": 120,
      "height": 20,
      "pattern": "vertical",
      "speed": 2,
      "distance": 100
    }
  ],
  "hazards": [
    {"x": 800, "y": 726, "width": 100, "height": 24, "type": "spike"}
  ],
  "collectibles": [
    {"x": 300, "y": 500, "type": "coin"},
    {"x": 600, "y": 400, "type": "powerup"}
  ],
  "checkpoint": {
    "x": 1000,
    "y": 200,
    "width": 40,
    "height": 60
  },
  "goal": {
    "x": 3500,
    "y": 700,
    "width": 50,
    "height": 50
  }
}
```

### Platform Types
- `normal` - Standard platform (gray)
- `ice` - Slippery platform (cyan)
- `sticky` - High friction platform (orange)
- `bouncy` - Launches player upward (purple)
- `fall` - Falls after player steps on it (light gray)
- `oneway` - Can jump through from below (yellow)

### Moving Platforms
Add these properties to create moving platforms:
- `pattern`: "horizontal", "vertical", "circular", or "square"
- `speed`: Movement speed (1-5 recommended)
- `distance`: How far to move (in pixels)

## Customization

You can easily customize the game by editing `constants.py`:

```python
# Physics
GRAVITY = 0.8                    # How fast you fall
PLAYER_MAX_SPEED = 6            # Running speed
PLAYER_JUMP_STRENGTH = -16       # Jump power
PLAYER_DASH_SPEED = 15          # Dash speed

# Player abilities
PLAYER_MAX_HEALTH = 3           # Starting health
PLAYER_DASH_COOLDOWN = 40       # Frames between dashes

# Screen size
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
```

## Future Enhancements

Possible additions for future development:
- Sound effects and background music
- Sprite graphics and animations
- Boss fights with multiple phases
- Additional enemy types
- Level editor
- Local co-op multiplayer
- Achievement system
- Save/load game progress
- More power-up types
- Additional level mechanics

## Development

This game was built with:
- **Python 3.x**
- **Pygame 2.5+**

The code is organized into modules for easy modification and extension:
- Each file handles a specific aspect of the game
- Platform and enemy types use inheritance for easy customization
- Level data is in JSON for easy level creation
- Constants are centralized for easy tweaking

## Credits

Built as a learning project to demonstrate:
- 2D platformer physics
- Particle systems
- Camera systems
- Entity-component patterns
- JSON-based level loading
- Game state management

## License

Free to use and modify for educational purposes!

---

Have fun playing and creating levels! Feel free to experiment with the code and make it your own.
