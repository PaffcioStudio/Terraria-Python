import pygame
from data.constants.constants import BLOCK_SIZE, BLOCK_PROPERTIES

class Mob:
    def __init__(self, x, y, sprite_sheet_path):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(self.x), int(self.y), 23, 23)  # Rozmiar klatki
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.health = 10
        self.state = "idle"  # idle, waking, walking, attacking
        self.frame = 0
        self.frame_timer = 0
        self.animations = self._load_animations(sprite_sheet_path)

    def _load_animations(self, sprite_sheet_path):
        """Wczytaj spritesheet i podziel na animacje."""
        try:
            sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            animations = {
                "waking": [sheet.subsurface((i * 23, 0, 23, 23)) for i in range(4)],
                "walking": [sheet.subsurface((i * 23, 23, 23, 23)) for i in range(4)],
                "attacking": [sheet.subsurface((i * 23, 46, 23, 23)) for i in range(2)]
            }
            return animations
        except pygame.error as e:
            print(f"Nie wczytano spritesheet {sprite_sheet_path}: {e}. Używam dummy.")
            dummy = pygame.Surface((23, 23))
            dummy.fill((0, 255, 0))  # Zielony prostokąt jako fallback
            return {
                "waking": [dummy] * 4,
                "walking": [dummy] * 4,
                "attacking": [dummy] * 2
            }

    def update(self, world, dt, player_x):
        """Aktualizuj stan mobka."""
        self.vel_y += 0.7 * dt * 60  # Grawitacja
        self.vel_y = min(self.vel_y, 25)
        self.x += self.vel_x * dt * 60
        self.rect.x = int(self.x)
        self._check_collision(world, 'x', dt)
        self.y += self.vel_y * dt * 60
        self.rect.y = int(self.y)
        self._check_collision(world, 'y', dt)
        self._update_state(player_x)
        self._update_animation(dt)

    def _check_collision(self, world, axis, dt):
        """Sprawdź kolizje."""
        temp_rect = self.rect.copy()
        if axis == 'x':
            if self.vel_x > 0:
                temp_rect.right = int(self.x + self.vel_x * dt * 60)
            else:
                temp_rect.left = int(self.x + self.vel_x * dt * 60)
        elif axis == 'y':
            if self.vel_y > 0:
                temp_rect.bottom = int(self.y + self.vel_y * dt * 60)
            else:
                temp_rect.top = int(self.y + self.vel_y * dt * 60)
        for bx in range(int(temp_rect.left // BLOCK_SIZE), int(temp_rect.right // BLOCK_SIZE) + 1):
            for by in range(int(temp_rect.top // BLOCK_SIZE), int(temp_rect.bottom // BLOCK_SIZE) + 1):
                if not (0 <= bx < world.world_width_blocks and 0 <= by < world.world_height_blocks):
                    continue
                block_id = world.get_block(bx, by)
                if BLOCK_PROPERTIES.get(block_id, {}).get('solid', False):
                    block_rect = pygame.Rect(bx * BLOCK_SIZE, by * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if temp_rect.colliderect(block_rect):
                        if axis == 'x':
                            if self.vel_x > 0:
                                self.x = block_rect.left - 23
                                temp_rect.right = block_rect.left
                            elif self.vel_x < 0:
                                self.x = block_rect.right
                                temp_rect.left = block_rect.right
                            self.vel_x = 0
                        elif axis == 'y':
                            if self.vel_y > 0:
                                self.y = block_rect.top - 23
                                temp_rect.bottom = block_rect.top
                                self.vel_y = 0
                                self.on_ground = True
                            elif self.vel_y < 0:
                                self.y = block_rect.bottom
                                temp_rect.top = block_rect.bottom
                                self.vel_y = 0
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def _update_state(self, player_x):
        """Zmieniaj stan w zależności od odległości od gracza."""
        dist = abs(player_x - self.x)
        if dist < 200 and self.state == "idle":
            self.state = "waking"
        elif dist < 100 and self.state in ["waking", "walking"]:
            self.state = "attacking"
            self.vel_x = 0
        elif dist > 300 and self.state != "idle":
            self.state = "idle"
        elif self.state == "walking":
            self.vel_x = -2 if player_x > self.x else 2

    def _update_animation(self, dt):
        """Aktualizuj klatki animacji."""
        self.frame_timer += dt
        if self.frame_timer >= 0.2:  # 0.2 sekundy na klatkę
            self.frame_timer = 0
            anim = self.animations.get(self.state, self.animations["walking"])
            self.frame = (self.frame + 1) % len(anim)
        if self.state == "waking" and self.frame == len(self.animations["waking"]) - 1:
            self.state = "walking"

    def draw(self, surface, camera):
        """Rysuj mobka."""
        anim = self.animations.get(self.state, self.animations["walking"])
        frame_surface = anim[self.frame]
        adjusted_rect = camera.apply(self.rect)
        surface.blit(frame_surface, (adjusted_rect.x, adjusted_rect.y))