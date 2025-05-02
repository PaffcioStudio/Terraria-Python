import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(255, 255, 255), text_align='center'):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.text_align = text_align
        self.disabled = False

    def draw(self, surface):
        """Rysuj przycisk."""
        if self.disabled:
            current_color = (50, 50, 50)
        else:
            current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect()
            if self.text_align == 'center':
                text_rect.center = self.rect.center
            elif self.text_align == 'left':
                text_rect.midleft = self.rect.midleft
                text_rect.x += 10
            elif self.text_align == 'right':
                text_rect.midright = self.rect.midright
                text_rect.x -= 10
            text_rect.clamp_ip(self.rect)
            surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Obsługuj zdarzenia przycisku."""
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return True
        return False