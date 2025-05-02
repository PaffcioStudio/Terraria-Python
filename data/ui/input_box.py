import pygame
import re

class InputBox:
    def __init__(self, x, y, width, height, font, text='', max_length=50, color_inactive=(150, 150, 150), color_active=(200, 200, 200), text_color=(0, 0, 0), background_color=(255, 255, 255), allowed_chars=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = text
        self.max_length = max_length
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.text_color = text_color
        self.background_color = background_color
        self.color = self.color_inactive
        self.active = False
        self.allowed_chars = allowed_chars

    def handle_event(self, event):
        """Obsługuj zdarzenia pola tekstowego."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_DELETE:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.text = ''
            else:
                if len(self.text) < self.max_length and event.unicode:
                    if self.allowed_chars is None or re.match(self.allowed_chars, event.unicode):
                        self.text += event.unicode

    def draw(self, surface):
        """Rysuj pole tekstowe."""
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2)
        txt_surface = self.font.render(self.text, True, self.text_color)
        text_x = self.rect.x + 5
        text_y = self.rect.y + (self.rect.height - txt_surface.get_height()) // 2
        surface.blit(txt_surface, (text_x, text_y), area=pygame.Rect(0, 0, self.rect.width - 10, self.rect.height))