import pygame
from data.constants.constants import BLOCK_SIZE

class Camera:
    def __init__(self, target_rect, screen_width, screen_height, world_width_blocks, world_height_blocks):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width_pixels = world_width_blocks * BLOCK_SIZE
        self.world_height_pixels = world_height_blocks * BLOCK_SIZE
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.smooth_factor = 0.1  # Stały współczynnik płynności
        self.update(target_rect)  # Inicjalizacja

    def update(self, target_rect):
        """Aktualizuj pozycję kamery, trzymając gracza w centrum."""
        target_center_x = target_rect.centerx
        target_center_y = target_rect.centery

        # Przesunięcie kamery, żeby gracz był w centrum
        target_offset_x = target_center_x - self.screen_width // 2
        target_offset_y = target_center_y - self.screen_height // 2

        # Płynne przejście (lerp)
        self.offset_x += (target_offset_x - self.offset_x) * self.smooth_factor
        self.offset_y += (target_offset_y - self.offset_y) * self.smooth_factor

        # Ograniczenie kamery do granic świata
        max_offset_x = self.world_width_pixels - self.screen_width
        max_offset_y = self.world_height_pixels - self.screen_height
        
        if max_offset_x < 0:
            self.offset_x = max_offset_x / 2.0
        else:
            self.offset_x = max(0.0, min(self.offset_x, float(max_offset_x)))
            
        if max_offset_y < 0:
            self.offset_y = max_offset_y / 2.0
        else:
            self.offset_y = max(0.0, min(self.offset_y, float(max_offset_y)))

        # Debugowanie pozycji kamery
        # print(f"Kamera: offset_x={self.offset_x:.2f}, offset_y={self.offset_y:.2f}, target_center_x={target_center_x:.2f}")

    def apply(self, rect):
        """Zastosuj przesunięcie kamery do prostokąta."""
        return rect.move(-int(self.offset_x), -int(self.offset_y))

    def apply_coords(self, x, y):
        """Zastosuj przesunięcie kamery do współrzędnych."""
        return x - int(self.offset_x), y - int(self.offset_y)

    def to_world_coords(self, screen_x, screen_y):
        """Konwertuj współrzędne ekranu na współrzędne świata."""
        return screen_x + self.offset_x, screen_y + self.offset_y