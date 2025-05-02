import os
import pickle
import random
import noise
import shutil
import pygame  # Dodany import
from data.constants.constants import (
    AIR, GRASS, DIRT, STONE, COAL_ORE, IRON_ORE, SAND, CACTUS,
    CHSIZE, SETTINGS_FILE, PLAYER_FILE, WORLDS_DIR,
    PERLIN_SCALE, PERLIN_OCTAVES, PERLIN_PERSISTENCE, PERLIN_LACUNARITY,
    TERRAIN_HEIGHT_VARIATION, BLOCK_SIZE
)
from data.world.chunk import Chunk

def world_to_chunk(world_x, world_y):
    """Konwertuj współrzędne świata na współrzędne chunka."""
    chunk_x = world_x // CHSIZE
    chunk_y = world_y // CHSIZE
    local_x = world_x % CHSIZE
    local_y = world_y % CHSIZE
    if world_x < 0:
        chunk_x = (world_x + 1) // CHSIZE - 1
        local_x = (world_x % CHSIZE + CHSIZE) % CHSIZE
    if world_y < 0:
        chunk_y = (world_y + 1) // CHSIZE - 1
        local_y = (world_y % CHSIZE + CHSIZE) % CHSIZE
    return chunk_x, chunk_y, local_x, local_y

class World:
    def __init__(self, world_name, seed, chunk_cols, chunk_rows, game=None):
        self.game = game
        self.world_name = world_name
        self.seed = seed % 10000000000
        self.chunk_cols = chunk_cols
        self.chunk_rows = chunk_rows
        self.world_width_blocks = self.chunk_cols * CHSIZE
        self.world_height_blocks = self.chunk_rows * CHSIZE
        self.world_width_pixels = self.world_width_blocks * BLOCK_SIZE
        self.world_height_pixels = self.world_height_blocks * BLOCK_SIZE
        self.chunks = {}
        self.world_path = os.path.join(WORLDS_DIR, world_name)
        self._ground_height_cache = {}
        self._biome_cache = {}
        os.makedirs(os.path.join(self.world_path, 'chunks'), exist_ok=True)
        self._precalculate_ground_heights()

    def _precalculate_ground_heights(self):
        """Oblicz wysokości terenu i biomy dla każdej kolumny X."""
        print("Pre-kalkulacja wysokości gruntu i biomów...")
        max_repeat = 10000
        repeat_width_scaled_float = min(self.world_width_blocks * PERLIN_SCALE, max_repeat)
        repeat_width_scaled_int = max(1, int(repeat_width_scaled_float))
        safe_seed = self.seed % 10000
        print(f"Używam bezpiecznego seeda: {safe_seed}")

        previous_height = None
        for world_x in range(self.world_width_blocks):
            perlin_input_x = ((world_x * PERLIN_SCALE) % max_repeat) / max_repeat
            try:
                height_noise = noise.pnoise1(
                    perlin_input_x,
                    octaves=PERLIN_OCTAVES,
                    persistence=PERLIN_PERSISTENCE,
                    lacunarity=PERLIN_LACUNARITY,
                    repeat=repeat_width_scaled_int,
                    base=safe_seed
                )
                biome_noise = noise.pnoise1(
                    perlin_input_x * 0.5,
                    octaves=PERLIN_OCTAVES,
                    persistence=PERLIN_PERSISTENCE,
                    lacunarity=PERLIN_LACUNARITY,
                    repeat=repeat_width_scaled_int,
                    base=safe_seed + 1
                )
            except Exception as e:
                print(f"Błąd w noise dla world_x {world_x}: {e}. Używam domyślnych wartości.")
                height_noise = 0.0
                biome_noise = 0.0

            ground_level_y = int(self.world_height_blocks * 0.6 + height_noise * self.world_height_blocks * TERRAIN_HEIGHT_VARIATION)
            ground_level_y = max(0, min(ground_level_y, self.world_height_blocks - 1))
            
            if previous_height is not None:
                max_diff = 3
                if abs(ground_level_y - previous_height) > max_diff:
                    ground_level_y = previous_height + max_diff if ground_level_y > previous_height else previous_height - max_diff
            previous_height = ground_level_y

            biome_type = self._determine_biome(biome_noise)
            self._ground_height_cache[world_x] = ground_level_y
            self._biome_cache[world_x] = biome_type
        print("Pre-kalkulacja zakończona.")

    def _determine_biome(self, biome_noise):
        """Określ typ biomu na podstawie wartości noise."""
        if biome_noise < -0.3:
            return "desert"
        elif biome_noise < 0.3:
            return "grassland"
        else:
            return "forest"

    def _generate_chunk_terrain(self, chunk):
        """Wygeneruj teren w chunku z uwzględnieniem biomów."""
        world_y_start_of_chunk = chunk.chunk_y * CHSIZE
        for local_x in range(chunk.width):
            world_x = chunk.chunk_x * CHSIZE + local_x
            ground_level_y = self._ground_height_cache.get(world_x)
            biome_type = self._biome_cache.get(world_x, "grassland")
            if ground_level_y is None:
                print(f"Brak wysokości dla world_x {world_x}. Pomijam kolumnę.")
                continue
            for local_y in range(chunk.height):
                world_y = world_y_start_of_chunk + local_y
                if world_y < ground_level_y:
                    chunk.set_block(local_x, local_y, AIR)
                elif world_y == ground_level_y:
                    if biome_type == "desert":
                        chunk.set_block(local_x, local_y, SAND)
                    elif biome_type == "forest":
                        chunk.set_block(local_x, local_y, GRASS)
                    else:
                        chunk.set_block(local_x, local_y, GRASS)
                elif world_y > ground_level_y and world_y <= ground_level_y + random.randint(3, 6):
                    if biome_type == "desert":
                        chunk.set_block(local_x, local_y, SAND)
                    else:
                        chunk.set_block(local_x, local_y, DIRT)
                else:
                    chunk.set_block(local_x, local_y, STONE)
                    if world_y > ground_level_y + 8:
                        random.seed(self.seed + world_x * 7 + world_y * 13)
                        if random.random() < 0.03:
                            chunk.set_block(local_x, local_y, COAL_ORE)
                        elif random.random() < 0.015:
                            chunk.set_block(local_x, local_y, IRON_ORE)

        # Generowanie szczegółów biomów
        random.seed(self.seed + chunk.chunk_x * 23 + chunk.chunk_y * 17 + 99)
        for local_x in range(chunk.width):
            world_x = chunk.chunk_x * CHSIZE + local_x
            ground_level_y = self._ground_height_cache.get(world_x)
            biome_type = self._biome_cache.get(world_x, "grassland")
            if ground_level_y is not None:
                world_y_at_chunk_top = chunk.chunk_y * CHSIZE
                if world_y_at_chunk_top <= ground_level_y < world_y_at_chunk_top + CHSIZE:
                    local_y_ground = ground_level_y % CHSIZE
                    if biome_type == "desert" and chunk.get_block(local_x, local_y_ground) == SAND:
                        if local_y_ground > 0 and chunk.get_block(local_x, local_y_ground - 1) == AIR:
                            if random.random() < 0.01:
                                chunk.set_block(local_x, local_y_ground - 1, CACTUS)
                                for height in range(1, random.randint(2, 4)):
                                    if local_y_ground - 1 - height >= 0 and chunk.get_block(local_x, local_y_ground - 1 - height) == AIR:
                                        chunk.set_block(local_x, local_y_ground - 1 - height, CACTUS)
                                    else:
                                        break
                    elif biome_type == "forest" and chunk.get_block(local_x, local_y_ground) == GRASS:
                        if random.random() < 0.05:
                            for dx in range(-1, 2):
                                for dy in range(-3, 0):
                                    nx_local = local_x + dx
                                    ny_local = local_y_ground + dy
                                    if 0 <= nx_local < chunk.width and 0 <= ny_local < chunk.height:
                                        if dy == -3:
                                            chunk.set_block(nx_local, ny_local, STONE)
                                        elif dy < 0:
                                            chunk.set_block(nx_local, ny_local, GRASS)

    def get_chunk(self, chunk_x, chunk_y):
        """Pobierz lub wygeneruj chunk."""
        if not (0 <= chunk_x < self.chunk_cols and 0 <= chunk_y < self.chunk_rows):
            return None
        chunk_coords = (chunk_x, chunk_y)
        if chunk_coords not in self.chunks:
            chunk = Chunk(chunk_x, chunk_y, CHSIZE, CHSIZE)
            if not chunk.load(self.world_path):
                self._generate_chunk_terrain(chunk)
                chunk.generated = True
                chunk.modified = True
            self.chunks[chunk_coords] = chunk
        return self.chunks[chunk_coords]

    def get_block(self, world_x, world_y):
        """Pobierz blok w współrzędnych świata."""
        if not (0 <= world_x < self.world_width_blocks and 0 <= world_y < self.world_height_blocks):
            return AIR
        chunk_x, chunk_y, local_x, local_y = world_to_chunk(world_x, world_y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        if chunk:
            return chunk.get_block(local_x, local_y)
        return AIR

    def set_block(self, world_x, world_y, block_id):
        """Ustaw blok w współrzędnych świata."""
        if not (0 <= world_x < self.world_width_blocks and 0 <= world_y < self.world_height_blocks):
            return False
        chunk_x, chunk_y, local_x, local_y = world_to_chunk(world_x, world_y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        if chunk:
            return chunk.set_block(local_x, local_y, block_id)
        return False

    def save_settings(self):
        """Zapisz ustawienia świata."""
        settings_path = os.path.join(self.world_path, SETTINGS_FILE)
        settings_data = {
            'world_name': self.world_name,
            'seed': self.seed,
            'chunk_cols': self.chunk_cols,
            'chunk_rows': self.chunk_rows,
        }
        try:
            with open(settings_path, 'wb') as f:
                pickle.dump(settings_data, f)
        except Exception as e:
            print(f"Błąd zapisu ustawień świata '{self.world_name}': {e}")

    def save_all_chunks(self):
        """Zapisz wszystkie zmodyfikowane chunki."""
        chunks_to_save = list(self.chunks.values())
        saved_count = 0
        for chunk in chunks_to_save:
            if chunk.save(self.world_path):
                saved_count += 1
        if saved_count > 0:
            print(f"Zapisano {saved_count} zmodyfikowanych chunków dla świata '{self.world_name}'.")

    def save(self, player_data):
        """Zapisz świat i dane gracza."""
        self.save_settings()
        self.save_all_chunks()
        self.save_player(player_data)
        print("Zapis zakończony.")

    def save_player(self, player_data):
        """Zapisz dane gracza."""
        player_file_path = os.path.join(self.world_path, PLAYER_FILE)
        try:
            with open(player_file_path, 'wb') as f:
                pickle.dump(player_data, f)
        except Exception as e:
            print(f"Błąd zapisu danych gracza dla świata '{self.world_name}': {e}")

    @staticmethod
    def load_world_settings(world_name):
        """Wczytaj ustawienia świata."""
        world_path = os.path.join(WORLDS_DIR, world_name)
        settings_path = os.path.join(world_path, SETTINGS_FILE)
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'rb') as f:
                    settings = pickle.load(f)
                    print(f"Załadowano ustawienia dla świata '{world_name}'.")
                    return settings
            except Exception as e:
                print(f"Błąd wczytania ustawień dla świata '{world_name}': {e}")
                return None
        return None

    @staticmethod
    def load_player_data(world_name):
        """Wczytaj dane gracza."""
        world_path = os.path.join(WORLDS_DIR, world_name)
        player_file_path = os.path.join(world_path, PLAYER_FILE)
        if os.path.exists(player_file_path):
            try:
                with open(player_file_path, 'rb') as f:
                    player_data = pickle.load(f)
                    print(f"Załadowano dane gracza dla świata '{world_name}'.")
                    return player_data
            except Exception as e:
                print(f"Błąd wczytania danych gracza dla świata '{world_name}': {e}")
                return None
        return None

    @staticmethod
    def delete_world_directory(world_name):
        """Usuń katalog świata."""
        world_path = os.path.join(WORLDS_DIR, world_name)
        if os.path.exists(world_path):
            try:
                print(f"Usuwanie świata '{world_name}'...")
                shutil.rmtree(world_path)
                print(f"Świat '{world_name}' usunięto.")
                return True
            except Exception as e:
                print(f"Błąd usuwania świata '{world_name}': {e}")
                return False
        print(f"Świat '{world_name}' nie znaleziono.")
        return False
    
    def render(self, screen, camera, block_textures=None):
        """Renderuje świat na ekranie względem kamery."""
        # Oblicz zakres kafelków widocznych na ekranie
        start_block_x = max(0, int(camera.offset_x // BLOCK_SIZE))
        start_block_y = max(0, int(camera.offset_y // BLOCK_SIZE))
        end_block_x = min(
            self.world_width_blocks,
            int((camera.offset_x + camera.screen_width) // BLOCK_SIZE + 1)
        )
        end_block_y = min(
            self.world_height_blocks,
            int((camera.offset_y + camera.screen_height) // BLOCK_SIZE + 1)
        )

        # Renderuj widoczne bloki
        for block_y in range(start_block_y, end_block_y):
            for block_x in range(start_block_x, end_block_x):
                block_id = self.get_block(block_x, block_y)
                if block_id != AIR:
                    block_screen_x = block_x * BLOCK_SIZE - camera.offset_x
                    block_screen_y = block_y * BLOCK_SIZE - camera.offset_y
                    
                    if (block_screen_x + BLOCK_SIZE > 0 and block_screen_x < camera.screen_width and
                        block_screen_y + BLOCK_SIZE > 0 and block_screen_y < camera.screen_height):
                        
                        if block_textures and block_id in block_textures:
                            screen.blit(
                                block_textures[block_id],
                                (block_screen_x, block_screen_y)
                            )
                        else:
                            block_colors = {
                                GRASS: (100, 200, 100),
                                DIRT: (150, 100, 50),
                                STONE: (100, 100, 100),
                                SAND: (230, 220, 150),
                                CACTUS: (0, 150, 0),
                                COAL_ORE: (50, 50, 50),
                                IRON_ORE: (200, 200, 200)
                            }
                            color = block_colors.get(block_id, (100, 100, 100))
                            pygame.draw.rect(
                                screen,
                                color,
                                (block_screen_x, block_screen_y, BLOCK_SIZE, BLOCK_SIZE)
                            )