# data/ui/toggle.py
import pygame

class Toggle:
    def __init__(self, x, y, width, height, initial_state, font, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state  # True (włączone), False (wyłączone)
        self.font = font
        self.label = label
        self.color_on = (50, 150, 50)
        self.color_off = (150, 50, 50)

    def handle_event(self, event):
        """Obsługuj kliknięcie."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False

    def draw(self, screen):
        """Rysuj przełącznik."""
        color = self.color_on if self.state else self.color_off
        pygame.draw.rect(screen, color, self.rect)
        label_surface = self.font.render(f"{self.label}: {'Wł' if self.state else 'Wył'}", True, (255, 255, 255))
        screen.blit(label_surface, (self.rect.x, self.rect.y - 30))