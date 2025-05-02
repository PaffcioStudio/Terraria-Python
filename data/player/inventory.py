import pygame
from data.constants.constants import BLOCK_SIZE, AIR, BLOCK_PROPERTIES, BLOCK_COLORS

class Inventory:
    def __init__(self, size=10):
        self.size = size
        self.slots = [(AIR, 0) for _ in range(self.size)]

    def add_item(self, block_id, count):
        """Dodaj przedmiot do inwentarza."""
        if block_id == AIR or not BLOCK_PROPERTIES.get(block_id, {}).get('collectable', False):
            return False
        if count <= 0:
            return True
        items_to_add = count
        for i in range(self.size):
            current_id, current_count = self.slots[i]
            if current_id == block_id and current_count < 64:
                stack_space = 64 - current_count
                add_amount = min(items_to_add, stack_space)
                self.slots[i] = (block_id, current_count + add_amount)
                items_to_add -= add_amount
                if items_to_add == 0:
                    return True
        if items_to_add > 0:
            for i in range(self.size):
                current_id, current_count = self.slots[i]
                if current_id == AIR:
                    add_amount = min(items_to_add, 64)
                    self.slots[i] = (block_id, add_amount)
                    items_to_add -= add_amount
                    if items_to_add == 0:
                        return True
        return items_to_add == 0

    def remove_item(self, slot_index, count=1):
        """Usuń przedmiot z inwentarza."""
        if count <= 0:
            return True
        if 0 <= slot_index < self.size:
            current_id, current_count = self.slots[slot_index]
            if current_count >= count:
                new_count = current_count - count
                self.slots[slot_index] = (current_id, new_count) if new_count > 0 else (AIR, 0)
                return True
        return False

    def get_selected_block(self, selected_slot_index):
        """Pobierz wybrany blok."""
        return self.slots[selected_slot_index] if 0 <= selected_slot_index < self.size else (AIR, 0)

    def get_data(self):
        """Pobierz dane inwentarza."""
        return {'slots': self.slots}

    def load_data(self, data):
        """Wczytaj dane inwentarza."""
        loaded_slots = data.get('slots', [(AIR, 0)] * self.size)
        self.slots = loaded_slots[:self.size] if len(loaded_slots) > self.size else loaded_slots + [(AIR, 0)] * (self.size - len(loaded_slots))
        print(f"Inwentarz załadowany: {len([id for id, count in self.slots if id != AIR])} slotów.")

    def draw(self, surface, screen_width, screen_height, selected_slot_index, block_textures):
        """Rysuj pasek inwentarza."""
        hotbar_height = BLOCK_SIZE + 14
        slot_size = BLOCK_SIZE + 12
        hotbar_width = slot_size * self.size + 4
        hotbar_x = (screen_width - hotbar_width) // 2
        hotbar_y = screen_height - hotbar_height
        hotbar_surface = pygame.Surface((hotbar_width, hotbar_height), pygame.SRCALPHA)
        hotbar_surface.fill((50, 50, 50, 180))
        surface.blit(hotbar_surface, (hotbar_x, hotbar_y))
        font = pygame.font.Font(None, 24)
        for i in range(self.size):
            slot_x_screen = hotbar_x + i * slot_size + 6
            slot_y_screen = hotbar_y + 6
            slot_rect_outer = pygame.Rect(slot_x_screen, slot_y_screen, BLOCK_SIZE + 2, BLOCK_SIZE + 2)
            slot_rect_inner = pygame.Rect(slot_x_screen + 1, slot_y_screen + 1, BLOCK_SIZE, BLOCK_SIZE)
            block_id, count = self.slots[i]
            if block_id != AIR:
                texture = block_textures.get(block_id)
                if texture:
                    surface.blit(texture, slot_rect_inner)
                elif block_id in BLOCK_COLORS:
                    pygame.draw.rect(surface, BLOCK_COLORS[block_id], slot_rect_inner)
                else:
                    pygame.draw.rect(surface, (255, 0, 255), slot_rect_inner)
            border_color = (255, 255, 255) if i == selected_slot_index else (150, 150, 150)
            pygame.draw.rect(surface, border_color, slot_rect_outer, 3)
            if count > 0:
                count_surface = font.render(str(count), True, (255, 255, 255))
                count_rect = count_surface.get_rect(bottomright=slot_rect_outer.bottomright)
                count_rect.clamp_ip(hotbar_surface.get_rect(topleft=(hotbar_x, hotbar_y)))
                surface.blit(count_surface, count_rect)