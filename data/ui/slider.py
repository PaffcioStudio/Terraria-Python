# data/ui/slider.py
import pygame

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, font, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_rect = pygame.Rect(x, y, 10, height)
        self.update_handle_position()
        self.font = font
        self.label = label
        self.dragging = False

    def update_handle_position(self):
        """Aktualizuj pozycję uchwytu na podstawie wartości."""
        range_width = self.rect.width - self.handle_rect.width
        value_ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.x = self.rect.x + int(value_ratio * range_width)

    def handle_event(self, event):
        """Obsługuj zdarzenia myszy."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = min(max(event.pos[0], self.rect.x), self.rect.x + self.rect.width - self.handle_rect.width)
            range_width = self.rect.width - self.handle_rect.width
            value_ratio = (mouse_x - self.rect.x) / range_width
            self.value = int(self.min_val + value_ratio * (self.max_val - self.min_val))
            self.update_handle_position()
        return self.dragging

    def draw(self, screen):
        """Rysuj suwak."""
        pygame.draw.rect(screen, (100, 100, 100), self.rect)  # Tło suwaka
        pygame.draw.rect(screen, (255, 255, 255), self.handle_rect)  # Uchwyt
        label_surface = self.font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))