import pygame
from data.ui.button import Button

class Dropdown:
    def __init__(self, x, y, width, height, options, font, default_option, color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.selected_option = default_option if default_option in options else options[0]
        self.is_open = False
        self.option_buttons = []
        for i, option in enumerate(self.options):
            btn_y = y + height + i * height
            self.option_buttons.append(Button(x, btn_y, width, height, option, font, color, hover_color, text_color, text_align='left'))

    def draw(self, surface):
        """Rysuj dropdown."""
        main_button_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, main_button_color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        text_surface = self.font.render(self.selected_option, True, self.text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)
        triangle_color = self.text_color
        triangle_x = self.rect.right - 15
        triangle_y = self.rect.centery
        if self.is_open:
            pygame.draw.polygon(surface, triangle_color, [(triangle_x - 5, triangle_y + 3), (triangle_x + 5, triangle_y + 3), (triangle_x, triangle_y - 3)])
        else:
            pygame.draw.polygon(surface, triangle_color, [(triangle_x - 5, triangle_y - 3), (triangle_x + 5, triangle_y - 3), (triangle_x, triangle_y + 3)])
        if self.is_open:
            for btn in self.option_buttons:
                btn.draw(surface)

    def handle_event(self, event):
        """Obsługuj zdarzenia dropdown."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            if self.is_open:
                for btn in self.option_buttons:
                    if btn.rect.collidepoint(event.pos):
                        self.selected_option = btn.text
                        self.is_open = False
                        return True
                if not self.rect.collidepoint(event.pos):
                    clicked_on_option = any(btn.rect.collidepoint(event.pos) for btn in self.option_buttons)
                    if not clicked_on_option:
                        self.is_open = False
                        return True
        if self.is_open and event.type == pygame.MOUSEMOTION:
            for btn in self.option_buttons:
                btn.handle_event(event)
        return False

    def get_selected_value(self):
        """Pobierz wybraną opcję."""
        return self.selected_option