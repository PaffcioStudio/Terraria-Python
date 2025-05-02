import pygame
from data.constants.constants import PLAYER_WIDTH, PLAYER_HEIGHT, GRAVITY, MAX_FALL_SPEED, BLOCK_SIZE, BLOCK_PROPERTIES
from data.player.inventory import Inventory

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(self.x), int(self.y), PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.is_jumping = False
        self.inventory = Inventory()
        self.selected_inventory_slot = 0
        # Ładowanie sprite'a gracza
        try:
            self.image = pygame.image.load('assets/player/player.png').convert_alpha()
            if self.image.get_size() != (PLAYER_WIDTH, PLAYER_HEIGHT):
                self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        except pygame.error as e:
            print(f"Nie wczytano player.png: {e}. Rysuję prostokąt.")
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill((255, 0, 0))  # Czerwony prostokąt jako fallback

    def update(self, world, dt):
        """Aktualizuj pozycję i kolizje gracza."""
        self.vel_y += GRAVITY * dt * 60
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        self.x += self.vel_x * dt * 60
        self.rect.x = int(self.x)
        self._check_collision(world, axis='x')
        self.y += self.vel_y * dt * 60
        self.rect.y = int(self.y)
        self._check_collision(world, axis='y')

        feet_y_check = int(self.rect.bottom + 2)
        on_ground_found = False
        for check_x_offset in [0, int(PLAYER_WIDTH / 2), int(PLAYER_WIDTH - 1)]:
            check_x = int(self.rect.left + check_x_offset)
            block_at_feet_coords = (check_x // BLOCK_SIZE, feet_y_check // BLOCK_SIZE)
            block_at_feet_id = world.get_block(*block_at_feet_coords)
            if BLOCK_PROPERTIES.get(block_at_feet_id, {}).get('solid', False):
                on_ground_found = True
                break
        self.on_ground = on_ground_found

        if self.on_ground and self.vel_y > 0:
            self.vel_y = 0
            self.is_jumping = False
        if not self.on_ground and self.vel_y > 0:
            self.is_jumping = False

    def _check_collision(self, world, axis):
        """Sprawdź kolizje na osi X lub Y."""
        temp_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_WIDTH, PLAYER_HEIGHT)
        min_bx = int(temp_rect.left // BLOCK_SIZE)
        max_bx = int(temp_rect.right // BLOCK_SIZE)
        min_by = int(temp_rect.top // BLOCK_SIZE)
        max_by = int(temp_rect.bottom // BLOCK_SIZE)

        if axis == 'x':
            if self.vel_x > 0: max_bx += 1
            elif self.vel_x < 0: min_bx -= 1
            check_range_x = range(min_bx, max_bx + 1)
            check_range_y = range(min_by, max_by + 1)
        elif axis == 'y':
            if self.vel_y > 0: max_by += 1
            elif self.vel_y < 0: min_by -= 1
            check_range_x = range(min_bx, max_bx + 1)
            check_range_y = range(min_by, max_by + 1)

        for block_x in check_range_x:
            for block_y in check_range_y:
                if not (0 <= block_x < world.world_width_blocks and 0 <= block_y < world.world_height_blocks):
                    continue
                block_id = world.get_block(block_x, block_y)
                if BLOCK_PROPERTIES.get(block_id, {}).get('solid', False):
                    block_rect = pygame.Rect(block_x * BLOCK_SIZE, block_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if temp_rect.colliderect(block_rect):
                        if axis == 'x':
                            if self.vel_x > 0:
                                self.x = block_rect.left - PLAYER_WIDTH - 0.01
                                temp_rect.right = block_rect.left
                            elif self.vel_x < 0:
                                self.x = block_rect.right + 0.01
                                temp_rect.left = block_rect.right
                            self.vel_x = 0.0
                        elif axis == 'y':
                            if self.vel_y > 0:
                                self.y = block_rect.top - PLAYER_HEIGHT - 0.01
                                temp_rect.bottom = block_rect.top
                                self.vel_y = 0.0
                                self.on_ground = True
                            elif self.vel_y < 0:
                                self.y = block_rect.bottom + 0.01
                                temp_rect.top = block_rect.bottom
                                self.vel_y = 0.0
                                self.is_jumping = False
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def jump(self):
        """Wykonaj skok."""
        if self.on_ground:
            self.vel_y = -15  # JUMP_STRENGTH
            self.on_ground = False
            self.is_jumping = True

    def get_data(self):
        """Pobierz dane gracza."""
        return {
            'x': self.x,
            'y': self.y,
            'inventory': self.inventory.get_data(),
            'selected_inventory_slot': self.selected_inventory_slot,
        }

    def load_data(self, data):
        """Wczytaj dane gracza."""
        self.x = float(data.get('x', self.x))
        self.y = float(data.get('y', self.y))
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.inventory.load_data(data.get('inventory', {}))
        self.selected_inventory_slot = data.get('selected_inventory_slot', 0)
        print("Dane gracza załadowane.")

    def render(self, screen, camera):
        """Renderuj gracza na ekranie z uwzględnieniem kamery."""
        screen.blit(self.image, camera.apply(self.rect))