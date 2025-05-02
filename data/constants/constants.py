import os

# --- Stałe gry ---
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
BLOCK_SIZE = 32

# Ustawienia chunków
CHSIZE = 16
MAX_RENDER_DISTANCE = 4

# Rozmiary światów
WORLD_SIZES = {
    "Mały": (10, 10),           # 160x160 bloków
    "Średni": (20, 15),         # 320x240 bloków
    "Duży": (40, 25),           # 640x400 bloków
    "Gigantyczny": (60, 40),    # 960x640 bloków
    "Kolosalny": (180, 150)     # 1280x800 bloków
}
DEFAULT_WORLD_SIZE_KEY = "Średni"

# Ustawienia gracza
PLAYER_WIDTH = BLOCK_SIZE * 0.9
PLAYER_HEIGHT = BLOCK_SIZE * 1.8
PLAYER_SPEED = 6
GRAVITY = 0.7
JUMP_STRENGTH = -15
MAX_FALL_SPEED = 25

# Interakcje
BLOCK_INTERACT_RANGE = BLOCK_SIZE * 5
BLOCK_BREAK_COOLDOWN = 300  # 0.3s w milisekundach
BLOCK_BREAK_ANIMATION_DURATION = 500  # 0.5s

# Typy bloków
AIR = 0
DIRT = 1
STONE = 2
GRASS = 3
COAL_ORE = 4
IRON_ORE = 5
WOOD = 6
SAND = 7
CACTUS = 8
COBBLESTONE = 9

# Właściwości bloków
BLOCK_PROPERTIES = {
    AIR: {'solid': False, 'collectable': False, 'texture': None},
    DIRT: {'solid': True, 'collectable': True, 'texture': 'blocks/dirt_block.png'},
    STONE: {'solid': True, 'collectable': True, 'texture': 'blocks/cobblestone_block.png'},
    GRASS: {'solid': True, 'collectable': True, 'texture': 'blocks/grass_block.png'},
    COAL_ORE: {'solid': True, 'collectable': True, 'texture': 'ores/coal_ore.png'},
    IRON_ORE: {'solid': True, 'collectable': True, 'texture': 'ores/iron_ore.png'},
    WOOD: {'solid': True, 'collectable': True, 'texture': None},
    SAND: {'solid': True, 'collectable': True, 'texture': 'blocks/sand_block.png'},
    CACTUS: {'solid': True, 'collectable': True, 'texture': 'blocks/cactus.png'},
    COBBLESTONE: {'solid': True, 'collectable': True, 'texture': 'blocks/cobblestone_block.png'},
}

# Kolory bloków (fallback)
BLOCK_COLORS = {
    AIR: (0, 0, 0, 0),
    DIRT: (139, 69, 19),
    STONE: (128, 128, 128),
    GRASS: (0, 128, 0),
    COAL_ORE: (50, 50, 50),
    IRON_ORE: (150, 100, 80),
    WOOD: (100, 70, 30),
    SAND: (245, 222, 179),
    CACTUS: (50, 205, 50),
    COBBLESTONE: (128, 128, 128),
}

# Ustawienia Perlin Noise
PERLIN_SCALE = 0.03
PERLIN_OCTAVES = 6
PERLIN_PERSISTENCE = 0.5
PERLIN_LACUNARITY = 2.0
TERRAIN_HEIGHT_VARIATION = 0.3

# Ścieżki
ASSET_DIR = "assets"
MENU_BACKGROUND_PATH = os.path.join(ASSET_DIR, "menu", "background.png")
SKY_TEXTURE_PATH = os.path.join(ASSET_DIR, "sky", "sky_day.png")
WORLDS_DIR = "worlds"
CHUNK_DIR_NAME = "chunks"
SETTINGS_FILE = "settings.dat"
PLAYER_FILE = "player.dat"

# Stany gry
STATE_MAIN_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_NEW_WORLD_MENU = 3
STATE_LOAD_WORLD_MENU = 4
STATE_CONFIRM_DELETE = 5
STATE_SETTINGS_MENU = 6

# Domyślne ustawienia
DEFAULT_MUSIC_ENABLED = True
DEFAULT_MUSIC_VOLUME = 50  # 0-100
DEFAULT_SOUND_ENABLED = True
DEFAULT_SOUND_VOLUME = 50  # 0-100
DEFAULT_RENDER_DISTANCE = 1  # Domyślna wartość renderowania
MAX_RENDER_DISTANCE = 5  # Maksymalna wartość renderowania
MIN_RENDER_DISTANCE = 1  # Minimalna wartość renderowania

# Nazwy światów
WORLD_NAME_POOL = [
    "Bezimienny", "Pustkowia", "Zaginiona Kraina", 
    "Nowy Eden", "Kres", "Świt", "Zmierzch", "Kolos"
]
WORLD_NAMES_PATH = os.path.join(ASSET_DIR, "scripts", "worlds.txt")