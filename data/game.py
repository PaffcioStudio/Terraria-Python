import pygame
import sys
import random
import os
import logging
import yaml
from data.constants.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE, WORLD_SIZES, DEFAULT_WORLD_SIZE_KEY,
    BLOCK_PROPERTIES, BLOCK_COLORS, ASSET_DIR, MENU_BACKGROUND_PATH, SKY_TEXTURE_PATH,
    WORLD_NAME_POOL, WORLD_NAMES_PATH, STATE_MAIN_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_NEW_WORLD_MENU, STATE_LOAD_WORLD_MENU, STATE_CONFIRM_DELETE, PLAYER_SPEED,
    BLOCK_INTERACT_RANGE, BLOCK_BREAK_ANIMATION_DURATION, MAX_RENDER_DISTANCE, CHSIZE,
    STATE_SETTINGS_MENU
)
from data.audio.audio_manager import AudioManager
from data.player.player import Player
from data.player.camera import Camera
from data.player.inventory import Inventory
from data.ui.button import Button
from data.ui.input_box import InputBox
from data.ui.dropdown import Dropdown
from data.ui.slider import Slider
from data.ui.toggle import Toggle
from data.world.world import World, world_to_chunk
from data.mobs.mob import Mob

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sandbox 2D")
        pygame.key.set_repeat(150, 30)
        
        self.clock = pygame.time.Clock()
        logging.basicConfig(filename='logs/game.log', level=logging.INFO, format='%(asctime)s - %(message)s')
        
        # Inicjalizacja atrybutów
        self.breaking_blocks = {}
        self.crafting_recipes = {}
        self.crafting_time = 0
        self.crafting_progress = 0
        self.is_crafting = False
        self.mobs = []
        self.game_time = 0
        self.current_sky = 'day'
        self.sky_transition = 0
        self.world_list_scroll = 0
        self.is_dragging_scrollbar = False
        self.scrollbar_offset_y = 0
        
        # Audio i nazwy światów
        self.audio_manager = AudioManager()
        self.world_name_pool = WORLD_NAME_POOL
        
        try:
            with open(WORLD_NAMES_PATH, 'r', encoding='utf-8') as f:
                self.world_name_pool = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Błąd wczytania {WORLD_NAMES_PATH}: {e}. Używam domyślnej listy.")
            
        self.state = STATE_MAIN_MENU
        self.world = None
        self.player = None
        self.camera = None
        self._confirm_delete_world_name = None
        
        # Czcionki
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.input_font = pygame.font.Font(None, 28)
        self.confirm_font = pygame.font.Font(None, 30)
        self.error_font = pygame.font.Font(None, 24)
        
        # Tekstury
        self.block_textures = self._load_block_textures()
        self.sky_texture = self._load_sky_texture('sky_day.png')
        self.trash_icon = pygame.image.load(os.path.join(ASSET_DIR, "gui", "buttons", "trash.png")).convert_alpha()
        self.trash_icon = pygame.transform.scale(self.trash_icon, (40, 40))
        self.refresh_icon = pygame.image.load(os.path.join(ASSET_DIR, "gui", "buttons", "refresh.png")).convert_alpha()
        self.refresh_icon = pygame.transform.scale(self.refresh_icon, (32, 32))
        self.menu_background_image = self._load_menu_background()
        
        # Tekstury nieba
        self.sky_textures = {
            'day': self._load_sky_texture('sky_day.png'),
            'dusk': self._load_sky_texture('sky_dusk.png'),
            'night': self._load_sky_texture('sky_night.png')
        }
        
        # Główne menu
        self.main_menu_buttons = [
            Button(SCREEN_WIDTH // 2 - 100, 200, 200, 50, "Nowy świat", self.menu_font),
            Button(SCREEN_WIDTH // 2 - 100, 260, 200, 50, "Wczytaj świat", self.menu_font),
            Button(SCREEN_WIDTH // 2 - 100, 320, 200, 50, "Ustawienia", self.menu_font),
            Button(SCREEN_WIDTH // 2 - 100, 380, 200, 50, "Wyjdź", self.menu_font),
        ]
        
        # Menu nowego świata
        self._world_size_options = list(WORLD_SIZES.keys())
        self._selected_world_size_key = DEFAULT_WORLD_SIZE_KEY
        random_world_name = random.choice(self.world_name_pool) if self.world_name_pool else "Nowy Świat"
        self.new_world_menu_elements = {
            "title": self.title_font.render("Stwórz nowy świat", True, (255, 255, 255)),
            "name_label": self.menu_font.render("Nazwa świata:", True, (255, 255, 255)),
            "seed_label": self.menu_font.render("Ziarno (opcjonalnie):", True, (255, 255, 255)),
            "size_label": self.menu_font.render("Rozmiar:", True, (255, 255, 255)),
            "name_input": InputBox(SCREEN_WIDTH // 2 - 150, 200, 300, 40, self.input_font, text=random_world_name, max_length=30, allowed_chars=r'[a-zA-Z0-9 ]'),
            "seed_input": InputBox(SCREEN_WIDTH // 2 - 150, 280, 300, 40, self.input_font, text=str(random.randint(100000, 999999)), max_length=10, allowed_chars=r'[0-9]'),
            "name_refresh_button": Button(SCREEN_WIDTH // 2 + 160, 200, 40, 40, "", self.input_font),
            "seed_refresh_button": Button(SCREEN_WIDTH // 2 + 160, 280, 40, 40, "", self.input_font),
            "size_dropdown": Dropdown(SCREEN_WIDTH // 2 - 150, 360, 150, 40, self._world_size_options, self.input_font, self._selected_world_size_key),
            "create_button": Button(SCREEN_WIDTH // 2 - 100, 450, 200, 50, "Stwórz", self.menu_font),
            "back_button": Button(SCREEN_WIDTH // 2 - 100, 510, 200, 50, "Wstecz", self.menu_font),
            "error_message": None,
        }
        
        # Menu wczytywania świata
        self.load_world_menu_elements = {
            "title": self.title_font.render("Wczytaj świat", True, (255, 255, 255)),
            "world_items": [],
            "back_button": Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70, 200, 50, "Wstecz", self.menu_font),
        }
        self._populate_load_world_menu()
        
        # Menu ustawień
        self.settings_menu_elements = {
            "title": self.title_font.render("Ustawienia", True, (255, 255, 255)),
            "music_toggle": Toggle(SCREEN_WIDTH // 2 - 50, 200, 100, 40, self.audio_manager.music_enabled, self.menu_font, "Muzyka"),
            "music_volume_slider": Slider(SCREEN_WIDTH // 2 - 100, 260, 200, 20, 0, 100, self.audio_manager.music_volume, self.menu_font, "Głośność muzyki"),
            "sound_toggle": Toggle(SCREEN_WIDTH // 2 - 50, 320, 100, 40, self.audio_manager.sound_enabled, self.menu_font, "Dźwięki"),
            "sound_volume_slider": Slider(SCREEN_WIDTH // 2 - 100, 380, 200, 20, 0, 100, self.audio_manager.sound_volume, self.menu_font, "Głośność dźwięków"),
            "back_button": Button(SCREEN_WIDTH // 2 - 100, 450, 200, 50, "Wstecz", self.menu_font),
        }
        
        # Dialog potwierdzenia
        self.confirm_dialog = {
            "background": pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
            "box_rect": pygame.Rect(0, 0, 400, 200),
            "message_label_line1": None,
            "message_label_line2": None,
            "yes_button": Button(0, 0, 120, 40, "Tak", self.menu_font, color=(50, 150, 50), hover_color=(70, 180, 70)),
            "no_button": Button(0, 0, 120, 40, "Nie", self.menu_font, color=(150, 50, 50), hover_color=(180, 70, 70)),
        }
        self.confirm_dialog["box_rect"].center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.confirm_dialog["yes_button"].rect.bottomleft = (self.confirm_dialog["box_rect"].centerx - 10 - self.confirm_dialog["yes_button"].rect.width, self.confirm_dialog["box_rect"].bottom - 20)
        self.confirm_dialog["no_button"].rect.bottomright = (self.confirm_dialog["box_rect"].centerx + 10 + self.confirm_dialog["no_button"].rect.width, self.confirm_dialog["box_rect"].bottom - 20)
        self.confirm_dialog["background"].fill((0, 0, 0, 180))
        
        # Menu pauzy
        self.pause_menu = {
            "background": pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA),
            "box_rect": pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 200),
            "title": self.title_font.render("Pauza", True, (255, 255, 255)),
            "continue_button": Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, 200, 50, "Kontynuuj", self.menu_font),
            "exit_button": Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 50, "Wyjdź do menu", self.menu_font)
        }
        self.pause_menu["background"].fill((0, 0, 0, 180))
        
        # Scrollbar
        self.scrollbar_rect = pygame.Rect(SCREEN_WIDTH - 20, 150, 10, SCREEN_HEIGHT - 150 - 70)
        self.scrollbar_handle = pygame.Rect(SCREEN_WIDTH - 20, 150, 10, 20)
        
        # Wczytanie przepisów craftingu na końcu inicjalizacji
        self._load_crafting_recipes()

    def _load_crafting_recipes(self):
        crafting_path = os.path.join('data', 'scripts', 'crafting', 'crafting.yaml')
        try:
            with open(crafting_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.crafting_recipes = data.get('recipes', {})
                logging.info("Pomyślnie wczytano przepisy craftingu.")
        except FileNotFoundError:
            logging.error(f"Nie znaleziono pliku {crafting_path}")
            self.crafting_recipes = {}
        except yaml.YAMLError as e:
            logging.error(f"Błąd parsowania YAML w {crafting_path}: {e}")
            self.crafting_recipes = {}

    def _load_block_textures(self):
        textures = {}
        for block_id, properties in BLOCK_PROPERTIES.items():
            texture_path = properties.get('texture')
            if texture_path:
                full_path = os.path.join(ASSET_DIR, texture_path)
                try:
                    image = pygame.image.load(full_path).convert_alpha()
                    if image.get_size() != (BLOCK_SIZE, BLOCK_SIZE):
                        image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
                    textures[block_id] = image
                except (pygame.error, FileNotFoundError) as e:
                    logging.error(f"Nie wczytano tekstury {full_path}: {e}. Używam koloru.")
        return textures

    def _load_sky_texture(self, filename='sky_day.png'):
        try:
            image = pygame.image.load(os.path.join(ASSET_DIR, 'sky', filename)).convert()
            if image.get_size() != (1000, 500):
                image = pygame.transform.scale(image, (1000, 500))
            return image
        except (pygame.error, FileNotFoundError) as e:
            logging.error(f"Nie wczytano tekstury nieba {filename}: {e}")
            return None

    def _load_menu_background(self):
        try:
            image = pygame.image.load(MENU_BACKGROUND_PATH).convert()
            image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            return image
        except (pygame.error, FileNotFoundError) as e:
            logging.error(f"Nie wczytano tła menu {MENU_BACKGROUND_PATH}: {e}. Bez tła.")
            return None

    def _populate_load_world_menu(self):
        self.load_world_menu_elements["world_items"] = []
        if not os.path.exists('worlds'):
            os.makedirs('worlds')
            return
        world_names = [d for d in os.listdir('worlds') if os.path.isdir(os.path.join('worlds', d))]
        self.world_list_scroll = 0
        self.max_scroll = max(0, len(world_names) * (50 + 10) - (SCREEN_HEIGHT - 150 - 70))
        y_offset = 150
        button_height = 50
        button_spacing = 10
        world_button_width = 300
        delete_button_width = 40
        for i, name in enumerate(world_names):
            world_btn_x = SCREEN_WIDTH // 2 - world_button_width // 2
            world_btn_y = y_offset + i * (button_height + button_spacing)
            world_btn = Button(world_btn_x, world_btn_y, world_button_width, button_height, name, self.menu_font, text_align='left')
            delete_btn_x = world_btn_x + world_button_width + 5
            delete_btn_y = world_btn_y
            delete_btn = Button(delete_btn_x, delete_btn_y, delete_button_width, button_height, "", self.menu_font, color=(150, 50, 50), hover_color=(180, 70, 70))
            self.load_world_menu_elements["world_items"].append((world_btn, delete_btn, name))

    def _render_new_world_menu(self):
        if self.menu_background_image:
            self.screen.blit(self.menu_background_image, (0, 0))
        else:
            self.screen.fill((0, 0, 50))
        elements = self.new_world_menu_elements
        self.screen.blit(elements["title"], elements["title"].get_rect(center=(SCREEN_WIDTH // 2, 100)))
        self.screen.blit(elements["name_label"], (elements["name_input"].rect.x, elements["name_input"].rect.y - 30))
        elements["name_input"].draw(self.screen)
        elements["name_refresh_button"].draw(self.screen)
        refresh_icon_x = elements["name_refresh_button"].rect.centerx - self.refresh_icon.get_width() // 2
        refresh_icon_y = elements["name_refresh_button"].rect.centery - self.refresh_icon.get_height() // 2
        self.screen.blit(self.refresh_icon, (refresh_icon_x, refresh_icon_y))
        
        self.screen.blit(elements["seed_label"], (elements["seed_input"].rect.x, elements["seed_input"].rect.y - 30))
        elements["seed_input"].draw(self.screen)
        elements["seed_refresh_button"].draw(self.screen)
        refresh_icon_x = elements["seed_refresh_button"].rect.centerx - self.refresh_icon.get_width() // 2
        refresh_icon_y = elements["seed_refresh_button"].rect.centery - self.refresh_icon.get_height() // 2
        self.screen.blit(self.refresh_icon, (refresh_icon_x, refresh_icon_y))
        
        self.screen.blit(elements["size_label"], (elements["size_dropdown"].rect.x, elements["size_dropdown"].rect.y - 30))
        elements["size_dropdown"].draw(self.screen)
        elements["create_button"].draw(self.screen)
        elements["back_button"].draw(self.screen)
        if elements["error_message"]:
            self.screen.blit(elements["error_message"], (elements["name_input"].rect.x, elements["name_input"].rect.y + elements["name_input"].rect.height + 5))

    def run(self):
        running = True
        dt = 0
        last_break_time = 0
        self.audio_manager.play_music()
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == STATE_CONFIRM_DELETE:
                    self._handle_confirm_delete_events(event)
                elif self.state == STATE_MAIN_MENU:
                    self._handle_main_menu_events(event)
                elif self.state == STATE_NEW_WORLD_MENU:
                    self._handle_new_world_menu_events(event)
                elif self.state == STATE_LOAD_WORLD_MENU:
                    self._handle_load_world_menu_events(event)
                elif self.state == STATE_PLAYING:
                    self._handle_playing_events(event, current_time, last_break_time)
                    self._handle_crafting_events(event)
                    last_break_time = current_time
                elif self.state == STATE_PAUSED:
                    self._handle_pause_events(event)
                elif self.state == STATE_SETTINGS_MENU:
                    self._handle_settings_menu_events(event)
                
                if event.type == pygame.MOUSEWHEEL and self.player:
                    self.player.selected_inventory_slot = (self.player.selected_inventory_slot - event.y) % self.player.inventory.size

            # Aktualizacja stanu gry
            if self.state == STATE_PLAYING:
                self._update_playing(dt)
                self._update_crafting(dt)
                self._update_sky(dt)
                self._spawn_mobs()
                
                for mob in self.mobs:
                    mob.update(self.world, dt, self.player.x)
                    
                for block_coords in list(self.breaking_blocks.keys()):
                    start_time = self.breaking_blocks[block_coords]
                    if current_time - start_time > BLOCK_BREAK_ANIMATION_DURATION:
                        del self.breaking_blocks[block_coords]

            # Renderowanie
            self._render_sky()  # Dodajemy renderowanie nieba
            self.screen.fill((0, 0, 0))  # Czyszczenie ekranu (opcjonalne, ale lepsze dla nieba)
            
            if self.state == STATE_MAIN_MENU:
                self._render_main_menu()
            elif self.state == STATE_NEW_WORLD_MENU:
                self._render_new_world_menu()
            elif self.state == STATE_LOAD_WORLD_MENU:
                self._render_load_world_menu()
            elif self.state == STATE_PLAYING:
                self._render_playing(current_time)
            elif self.state == STATE_PAUSED:
                self._render_pause_menu()
            elif self.state == STATE_CONFIRM_DELETE:
                self._render_load_world_menu()
                self._render_confirm_delete_dialog()
            elif self.state == STATE_SETTINGS_MENU:
                self._render_settings_menu()
                
            pygame.display.flip()
        
        self.quit()

    def _handle_main_menu_events(self, event):
        for button in self.main_menu_buttons:
            if button.handle_event(event):
                self.audio_manager.play_sound('click')
                if button.text == "Nowy świat":
                    random_world_name = random.choice(self.world_name_pool) if self.world_name_pool else "Nowy Świat"
                    self.new_world_menu_elements["name_input"].text = random_world_name
                    self.new_world_menu_elements["seed_input"].text = str(random.randint(100000, 999999))
                    self.new_world_menu_elements["size_dropdown"].selected_option = DEFAULT_WORLD_SIZE_KEY
                    self.new_world_menu_elements["size_dropdown"].is_open = False
                    self.new_world_menu_elements["error_message"] = None
                    self.state = STATE_NEW_WORLD_MENU
                elif button.text == "Wczytaj świat":
                    self._populate_load_world_menu()
                    self.state = STATE_LOAD_WORLD_MENU
                elif button.text == "Ustawienia":
                    self.state = STATE_SETTINGS_MENU
                elif button.text == "Wyjdź":
                    self.quit()

    def _handle_new_world_menu_events(self, event):
        elements = self.new_world_menu_elements
        dropdown_handled = elements["size_dropdown"].handle_event(event)
        if not elements["size_dropdown"].is_open and not dropdown_handled:
            elements["name_input"].handle_event(event)
            elements["seed_input"].handle_event(event)
            if elements["name_refresh_button"].handle_event(event):
                self.audio_manager.play_sound('click')
                if self.world_name_pool:
                    new_name = random.choice(self.world_name_pool)
                    elements["name_input"].text = new_name[:30]
                else:
                    logging.info("Brak nazw do losowania!")
            if elements["seed_refresh_button"].handle_event(event):
                self.audio_manager.play_sound('click')
                elements["seed_input"].text = str(random.randint(100000, 999999))
            if elements["create_button"].handle_event(event):
                self.audio_manager.play_sound('click')
                world_name = elements["name_input"].text.strip()
                seed_str = elements["seed_input"].text.strip()
                selected_size_key = elements["size_dropdown"].get_selected_value()
                if not world_name:
                    elements["error_message"] = self.error_font.render("Nazwa świata nie może być pusta!", True, (255, 50, 50))
                    return
                if os.path.exists(os.path.join('worlds', world_name)):
                    elements["error_message"] = self.error_font.render("Taki świat już istnieje!", True, (255, 50, 50))
                    return
                seed = random.randint(100000, 999999)
                if seed_str:
                    try:
                        seed = abs(int(seed_str)) % 10000000000
                    except ValueError:
                        logging.info(f"Nie sparsowałem ziarna '{seed_str}'. Losowe ziarno.")
                        seed = random.randint(100000, 999999)
                chunk_width, chunk_height = WORLD_SIZES.get(selected_size_key, WORLD_SIZES[DEFAULT_WORLD_SIZE_KEY])
                self.start_new_world(world_name, seed, chunk_width, chunk_height)
            if elements["back_button"].handle_event(event):
                self.audio_manager.play_sound('click')
                self.state = STATE_MAIN_MENU
        elements["create_button"].disabled = not elements["name_input"].text.strip() or os.path.exists(os.path.join('worlds', elements["name_input"].text.strip()))

    def _handle_load_world_menu_events(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.world_list_scroll -= event.y * 20
            self.world_list_scroll = max(0, min(self.world_list_scroll, self.max_scroll))
            scroll_factor = self.max_scroll / (self.scrollbar_rect.height - self.scrollbar_handle.height) if self.max_scroll > 0 else 1
            self.scrollbar_handle.y = 150 + (self.world_list_scroll / scroll_factor)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(f"Kliknięto w: {event.pos}")  # Debugowanie pozycji kliknięcia
            # Sprawdź pasek przewijania
            if self.scrollbar_handle.collidepoint(event.pos):
                self.is_dragging_scrollbar = True
                self.scrollbar_offset_y = event.pos[1] - self.scrollbar_handle.y
                return

            # Sprawdź przyciski światów
            for world_btn, delete_btn, world_name in self.load_world_menu_elements["world_items"]:
                # Oblicz pozycję z przewijaniem
                world_btn_adjusted_y = world_btn.rect.y - self.world_list_scroll
                delete_btn_adjusted_y = delete_btn.rect.y - self.world_list_scroll
                world_btn_rect = world_btn.rect.copy()
                delete_btn_rect = delete_btn.rect.copy()
                world_btn_rect.y = world_btn_adjusted_y
                delete_btn_rect.y = delete_btn_adjusted_y

                print(f"Sprawdzam świat: {world_name}, world_btn_rect: {world_btn_rect}, delete_btn_rect: {delete_btn_rect}")  # Debugowanie

                if world_btn_rect.collidepoint(event.pos):
                    if world_btn.handle_event(event):
                        self.audio_manager.play_sound('click')
                        self.load_world(world_name)
                        return
                if delete_btn_rect.collidepoint(event.pos):
                    if delete_btn.handle_event(event):
                        self.audio_manager.play_sound('click')
                        self._confirm_delete_world_name = world_name
                        self.state = STATE_CONFIRM_DELETE
                        return

            # Sprawdź przycisk "Wstecz"
            if self.load_world_menu_elements["back_button"].handle_event(event):
                self.audio_manager.play_sound('click')
                self.state = STATE_MAIN_MENU
                return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging_scrollbar = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging_scrollbar:
            new_y = event.pos[1] - self.scrollbar_offset_y
            scroll_range = self.scrollbar_rect.height - self.scrollbar_handle.height
            new_y = max(self.scrollbar_rect.top, min(new_y, self.scrollbar_rect.bottom - self.scrollbar_handle.height))
            self.scrollbar_handle.y = new_y
            scroll_factor = self.max_scroll / scroll_range if scroll_range > 0 else 1
            self.world_list_scroll = (new_y - self.scrollbar_rect.top) * scroll_factor
            self.world_list_scroll = max(0, min(self.world_list_scroll, self.max_scroll))

    def _handle_confirm_delete_events(self, event):
        elements = self.confirm_dialog
        if elements["yes_button"].handle_event(event):
            self.audio_manager.play_sound('click')
            if self._confirm_delete_world_name:
                World.delete_world_directory(self._confirm_delete_world_name)
                self._confirm_delete_world_name = None
                self._populate_load_world_menu()
                self.state = STATE_LOAD_WORLD_MENU
            else:
                self.state = STATE_LOAD_WORLD_MENU
        elif elements["no_button"].handle_event(event):
            self.audio_manager.play_sound('click')
            self._confirm_delete_world_name = None
            self.state = STATE_LOAD_WORLD_MENU

    def _handle_playing_events(self, event, current_time, last_break_time):
        if not self.player or not self.world or not self.camera:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED if self.state == STATE_PLAYING else STATE_PLAYING
                return
        if self.state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_SPACE) and self.player.on_ground:
                    self.player.jump()
                    self.audio_manager.play_sound('jump')
                if pygame.K_1 <= event.key <= pygame.K_9:
                    slot_index = event.key - pygame.K_1
                    if slot_index < self.player.inventory.size:
                        self.player.selected_inventory_slot = slot_index
                if event.key == pygame.K_0 and self.player.inventory.size >= 10:
                    self.player.selected_inventory_slot = 9
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_world_x, mouse_world_y = self.camera.to_world_coords(*event.pos)
                target_block_x = int(mouse_world_x // BLOCK_SIZE)
                target_block_y = int(mouse_world_y // BLOCK_SIZE)
                if not (0 <= target_block_x < self.world.world_width_blocks and 0 <= target_block_y < self.world.world_height_blocks):
                    return
                player_center_world_x = self.player.x + 28.8 / 2.0
                player_center_world_y = self.player.y + 57.6 / 2.0
                block_center_world_x = target_block_x * BLOCK_SIZE + BLOCK_SIZE / 2.0
                block_center_world_y = target_block_y * BLOCK_SIZE + BLOCK_SIZE / 2.0
                dist_sq = (block_center_world_x - player_center_world_x)**2 + (block_center_world_y - player_center_world_y)**2
                if dist_sq > BLOCK_INTERACT_RANGE**2:
                    return
                if event.button == 1:
                    block_to_break_id = self.world.get_block(target_block_x, target_block_y)
                    if block_to_break_id != 0 and BLOCK_PROPERTIES.get(block_to_break_id, {}).get('solid', False):
                        if (target_block_x, target_block_y) not in self.breaking_blocks:
                            self.breaking_blocks[(target_block_x, target_block_y)] = current_time
                            if BLOCK_PROPERTIES.get(block_to_break_id, {}).get('collectable', False):
                                self.player.inventory.add_item(block_to_break_id, 1)
                            self.world.set_block(target_block_x, target_block_y, 0)
                elif event.button == 3:
                    selected_block_id, selected_block_count = self.player.inventory.get_selected_block(self.player.selected_inventory_slot)
                    if selected_block_id != 0 and selected_block_count > 0 and BLOCK_PROPERTIES.get(selected_block_id, {}).get('solid', False):
                        current_block_at_target = self.world.get_block(target_block_x, target_block_y)
                        potential_block_rect = pygame.Rect(target_block_x * BLOCK_SIZE, target_block_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        if self.player.rect.colliderect(potential_block_rect):
                            return
                        if current_block_at_target == 0:
                            success = self.world.set_block(target_block_x, target_block_y, selected_block_id)
                            if success:
                                self.player.inventory.remove_item(self.player.selected_inventory_slot, 1)

    def _handle_pause_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = STATE_PLAYING
            return
        if self.pause_menu["continue_button"].handle_event(event):
            self.audio_manager.play_sound('click')
            self.state = STATE_PLAYING
        if self.pause_menu["exit_button"].handle_event(event):
            self.audio_manager.play_sound('click')
            self.world.save(self.player.get_data())
            self.world.chunks.clear()
            self.world = None
            self.player = None
            self.camera = None
            self.state = STATE_MAIN_MENU
            self.audio_manager.play_music()

    def _handle_settings_menu_events(self, event):
        elements = self.settings_menu_elements
        if elements["back_button"].handle_event(event):
            self.audio_manager.play_sound('click')
            self.state = STATE_MAIN_MENU
            return
        
        if elements["music_toggle"].handle_event(event):
            self.audio_manager.toggle_music(elements["music_toggle"].state)
        if elements["sound_toggle"].handle_event(event):
            self.audio_manager.toggle_sound(elements["sound_toggle"].state)
        
        if elements["music_volume_slider"].handle_event(event):
            self.audio_manager.set_music_volume(elements["music_volume_slider"].value)
        if elements["sound_volume_slider"].handle_event(event):
            self.audio_manager.set_sound_volume(elements["sound_volume_slider"].value)

    def _render_settings_menu(self):
        if self.menu_background_image:
            self.screen.blit(self.menu_background_image, (0, 0))
        else:
            self.screen.fill((0, 0, 50))
        
        elements = self.settings_menu_elements
        self.screen.blit(elements["title"], elements["title"].get_rect(center=(SCREEN_WIDTH // 2, 100)))
        
        elements["music_toggle"].draw(self.screen)
        elements["music_volume_slider"].draw(self.screen)
        elements["sound_toggle"].draw(self.screen)
        elements["sound_volume_slider"].draw(self.screen)
        elements["back_button"].draw(self.screen)

    def _update_playing(self, dt):
        if self.player and self.world and self.camera and self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            moving_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            moving_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            self.player.vel_x = -PLAYER_SPEED if moving_left and not moving_right else PLAYER_SPEED if moving_right and not moving_left else 0
            self.player.update(self.world, dt)
            self.camera.update(self.player.rect)

    def _render_main_menu(self):
        if self.menu_background_image:
            self.screen.blit(self.menu_background_image, (0, 0))
        else:
            self.screen.fill((0, 0, 50))
        title_surface = self.title_font.render("Gra Sandbox", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        for button in self.main_menu_buttons:
            button.draw(self.screen)

    def _render_load_world_menu(self):
        if self.menu_background_image:
            self.screen.blit(self.menu_background_image, (0, 0))
        else:
            self.screen.fill((0, 0, 50))
        elements = self.load_world_menu_elements
        self.screen.blit(elements["title"], elements["title"].get_rect(center=(SCREEN_WIDTH // 2, 100)))
        for i, (world_btn, delete_btn, world_name) in enumerate(elements["world_items"]):
            adjusted_y = world_btn.rect.y - self.world_list_scroll
            if 150 <= adjusted_y <= SCREEN_HEIGHT - 70:
                world_btn.rect.y = adjusted_y
                delete_btn.rect.y = adjusted_y
                world_btn.draw(self.screen)
                delete_btn.draw(self.screen)
                trash_icon_x = delete_btn.rect.centerx - self.trash_icon.get_width() // 2
                trash_icon_y = delete_btn.rect.centery - self.trash_icon.get_height() // 2
                self.screen.blit(self.trash_icon, (trash_icon_x, trash_icon_y))
                world_btn.rect.y = world_btn.rect.y + self.world_list_scroll
                delete_btn.rect.y = delete_btn.rect.y + self.world_list_scroll
        elements["back_button"].draw(self.screen)
        pygame.draw.rect(self.screen, (100, 100, 100), self.scrollbar_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), self.scrollbar_handle)

    def _render_playing(self, current_time):
        self.screen.fill((0, 0, 0))  # Czyszczenie ekranu
        self._render_sky()  # Renderowanie nieba przed biomem
        if self.world and self.camera:
            player_chunk_x, player_chunk_y, _, _ = world_to_chunk(int(self.player.x // BLOCK_SIZE), int(self.player.y // BLOCK_SIZE))
            chunk = self.world.get_chunk(player_chunk_x, player_chunk_y)
            if chunk:
                world_x = player_chunk_x * CHSIZE
                biome_type = self.world._biome_cache.get(world_x, "grassland")
                if biome_type == "desert":
                    self.screen.fill((220, 200, 150))
                elif biome_type == "forest":
                    self.screen.fill((50, 150, 50))
                else:
                    self.screen.fill((100, 200, 100))
                self.world.render(self.screen, self.camera, self.block_textures)
        if self.player:
            self.player.render(self.screen, self.camera)
        for mob in self.mobs:
            mob.draw(self.screen, self.camera)
        if self.is_crafting:
            pygame.draw.rect(self.screen, (50, 50, 50), (SCREEN_WIDTH // 2 - 100, 50, 200, 20))
            progress_width = 200 * (self.crafting_progress / self.crafting_recipes[list(self.crafting_recipes.keys())[0]]['time'])
            pygame.draw.rect(self.screen, (0, 255, 0), (SCREEN_WIDTH // 2 - 100, 50, progress_width, 20))
        for block_coords, start_time in self.breaking_blocks.items():
            x, y = block_coords
            progress = min(1.0, (current_time - start_time) / BLOCK_BREAK_ANIMATION_DURATION)
            pygame.draw.rect(
                self.screen,
                (255, 0, 0),
                (x * BLOCK_SIZE - self.camera.offset_x, y * BLOCK_SIZE - self.camera.offset_y, BLOCK_SIZE * progress, BLOCK_SIZE),
                2
            )
        if self.player and self.player.inventory:
            self.player.inventory.draw(
                self.screen,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.player.selected_inventory_slot,
                self.block_textures
            )

    def _render_pause_menu(self):
        self.screen.blit(self.pause_menu["background"], (0, 0))
        self.screen.blit(self.pause_menu["title"], self.pause_menu["title"].get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))
        self.pause_menu["continue_button"].draw(self.screen)
        self.pause_menu["exit_button"].draw(self.screen)

    def _render_confirm_delete_dialog(self):
        self.screen.blit(self.confirm_dialog["background"], (0, 0))
        pygame.draw.rect(self.screen, (50, 50, 50), self.confirm_dialog["box_rect"])
        if self._confirm_delete_world_name:
            self.confirm_dialog["message_label_line1"] = self.confirm_font.render(f"Czy usunąć świat {self._confirm_delete_world_name}?", True, (255, 255, 255))
            self.confirm_dialog["message_label_line2"] = self.confirm_font.render("Ta operacja jest nieodwracalna!", True, (255, 100, 100))
        if self.confirm_dialog["message_label_line1"]:
            # Rozdzielamy ustawianie centerx i top
            label_rect1 = self.confirm_dialog["message_label_line1"].get_rect()
            label_rect1.centerx = self.confirm_dialog["box_rect"].centerx
            label_rect1.top = self.confirm_dialog["box_rect"].top + 20
            self.screen.blit(self.confirm_dialog["message_label_line1"], label_rect1)
        if self.confirm_dialog["message_label_line2"]:
            # To samo dla drugiej linii
            label_rect2 = self.confirm_dialog["message_label_line2"].get_rect()
            label_rect2.centerx = self.confirm_dialog["box_rect"].centerx
            label_rect2.top = self.confirm_dialog["box_rect"].top + 60
            self.screen.blit(self.confirm_dialog["message_label_line2"], label_rect2)
        self.confirm_dialog["yes_button"].draw(self.screen)
        self.confirm_dialog["no_button"].draw(self.screen)

    def _handle_crafting_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c and not self.is_crafting:
            if self._can_craft('workbench'):
                self.is_crafting = True
                self.crafting_progress = 0
                self.audio_manager.play_sound('craft')

    def _can_craft(self, recipe_name):
        recipe = self.crafting_recipes.get(recipe_name)
        if not recipe:
            return False
        inventory = self.player.inventory
        for ingredient in recipe.get('ingredients', []):
            block_id = ingredient['id']
            count_needed = ingredient['count']
            has_enough = False
            for slot_id, slot_count in enumerate(inventory.slots):
                if slot_id == block_id and slot_count >= count_needed:
                    has_enough = True
                    break
            if not has_enough:
                return False
        return True

    def _update_crafting(self, dt):
        if self.is_crafting:
            recipe = next((r for r in self.crafting_recipes.values() if self._can_craft(list(self.crafting_recipes.keys())[list(self.crafting_recipes.values()).index(r)])), None)
            if recipe:
                self.crafting_progress += dt
                if self.crafting_progress >= recipe.get('time', 1):
                    self._finish_crafting(recipe)
            else:
                self.is_crafting = False

    def _finish_crafting(self, recipe):
        result = recipe.get('result')
        if result:
            self.player.inventory.add_item(result, 1)
            for ingredient in recipe.get('ingredients', []):
                self.player.inventory.remove_item(self.player.selected_inventory_slot, ingredient['count'])
        self.is_crafting = False
        self.crafting_progress = 0
        logging.info(f"Ukończono craftowanie: {result}")

    def _update_sky(self, dt):
        self.game_time += dt
        time_24h = (self.game_time / 1200) % 24
        if 6 <= time_24h < 18:
            target_sky = 'day'
        elif 18 <= time_24h < 20 or 4 <= time_24h < 6:
            target_sky = 'dusk'
        else:
            target_sky = 'night'
        if self.current_sky != target_sky:
            self.sky_transition += dt / 5
            if self.sky_transition >= 1:
                self.current_sky = target_sky
                self.sky_transition = 0
        else:
            self.sky_transition = max(0, self.sky_transition - dt / 5)

    def _render_sky(self):
        if not self.sky_textures[self.current_sky]:
            self.screen.fill((0, 0, 50))
            return
            
        next_sky = 'dusk' if self.current_sky == 'day' else 'day' if self.current_sky == 'dusk' else 'dusk'
        base_surface = self.sky_textures[self.current_sky]
        next_surface = self.sky_textures[next_sky]
        
        if self.sky_transition > 0 and next_surface:
            blend_surface = base_surface.copy()
            blend_surface.blit(next_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            alpha = int(self.sky_transition * 255)
            blend_surface.set_alpha(alpha)
            self.screen.blit(blend_surface, ((SCREEN_WIDTH - 1000) // 2, (SCREEN_HEIGHT - 500) // 2))
        else:
            self.screen.blit(base_surface, ((SCREEN_WIDTH - 1000) // 2, (SCREEN_HEIGHT - 500) // 2))
        
        time_24h = (self.game_time / 1200) % 24
        hour = int(time_24h)
        minute = int((time_24h % 1) * 60)
        time_str = f"{hour:02d}:{minute:02d}"
        clock_surface = self.menu_font.render(time_str, True, (255, 255, 255))
        clock_rect = clock_surface.get_rect(centerx=SCREEN_WIDTH // 2, top=10)
        self.screen.blit(clock_surface, clock_rect)

    def _spawn_mobs(self):
        if random.random() < 0.01 and self.world:
            chunk_x, chunk_y, _, _ = world_to_chunk(
                random.randint(0, self.world.world_width_blocks),
                random.randint(0, self.world.world_height_blocks)
            )
            chunk = self.world.get_chunk(chunk_x, chunk_y)
            if chunk:
                local_x = random.randint(0, CHSIZE - 1) * BLOCK_SIZE
                local_y = random.randint(0, CHSIZE - 1) * BLOCK_SIZE
                world_x = chunk_x * CHSIZE + local_x // BLOCK_SIZE
                biome_type = self.world._biome_cache.get(world_x, "grassland")
                
                if biome_type == "forest" and random.random() < 0.05:
                    self.mobs.append(Mob(
                        local_x + chunk_x * CHSIZE * BLOCK_SIZE,
                        local_y + chunk_y * CHSIZE * BLOCK_SIZE,
                        'assets/mobs/slime_green/slime_green.png'
                    ))

    def start_new_world(self, world_name, seed, chunk_width, chunk_height):
        self.world = World(world_name, seed, chunk_width, chunk_height)
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.camera = Camera(self.player.rect, SCREEN_WIDTH, SCREEN_HEIGHT, 
                           self.world.world_width_blocks, self.world.world_height_blocks)
        self.state = STATE_PLAYING
        self.mobs = []
        self.audio_manager.stop_music()

    def load_world(self, world_name):
        self.world = World.load(world_name)
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.camera = Camera(self.player.rect, SCREEN_WIDTH, SCREEN_HEIGHT,
                           self.world.world_width_blocks, self.world.world_height_blocks)
        self.state = STATE_PLAYING
        self.mobs = []
        self.audio_manager.stop_music()

    def quit(self):
        if self.world:
            self.world.save(self.player.get_data())
        pygame.quit()
        sys.exit()