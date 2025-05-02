
# 2D Terraria-like Sandbox Game

A Python-based 2D sandbox game inspired by Terraria, featuring world generation, crafting, inventory system, and mobs. Built with Pygame.

## Features

- 🌍 Procedural world generation with different biomes (grassland, desert, forest)
- ⛏️ Mining and building system with various block types
- 🎒 Inventory system with 10 slots
- ⚒️ Crafting system (workbench recipe included)
- 🎮 Player physics with jumping and movement
- 🌅 Day-night cycle with dynamic sky rendering
- 🔊 Audio system with background music and sound effects
- 🏡 World saving/loading functionality
- 🎚️ Settings menu with audio controls

## Technologies Used

- Python 3.8+
- Pygame 2.0+
- PyYAML (for crafting recipes)
- Perlin noise (for terrain generation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/terraria-2d-clone.git
   cd terraria-2d-clone
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Create `requirements.txt` with: `pygame`, `PyYAML`, `noise`)*

3. Run the game:
   ```bash
   python main.py
   ```

## Controls

- **W/Space**: Jump
- **A/D or Left/Right**: Move horizontally
- **Left Click**: Break blocks
- **Right Click**: Place blocks
- **1-9**: Select inventory slots
- **ESC**: Pause game/open menu
- **Mouse Wheel**: Cycle through inventory

## File Structure

```
.
├── assets/              # Game assets (images, sounds)
├── data/                # Game logic and systems
│   ├── audio/           # Audio management
│   ├── constants/       # Game constants
│   ├── mobs/            # Mob AI and behavior
│   ├── player/          # Player controls and inventory
│   ├── ui/              # UI elements
│   ├── world/           # World generation and chunks
│   └── game.py          # Main game class
├── main.py              # Entry point
└── README.md            # This file
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See LICENSE for more information.

## Known Issues

- Some mob textures are missing
- Crafting system is basic (only workbench implemented)
- Limited biome variety

## Future Plans

- More mobs and enemies
- Expanded crafting system
- Additional biomes and blocks
- Multiplayer support
- Weather system
