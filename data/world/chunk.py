import pickle
import os
from data.constants.constants import AIR, CHSIZE

class Chunk:
    def __init__(self, chunk_x, chunk_y, chunk_width_blocks, chunk_height_blocks):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.width = chunk_width_blocks
        self.height = chunk_height_blocks
        self.blocks = [[AIR for _ in range(self.height)] for _ in range(self.width)]
        self.generated = False
        self.modified = False

    def get_block(self, local_x, local_y):
        """Pobierz blok w lokalnych współrzędnych."""
        if 0 <= local_x < self.width and 0 <= local_y < self.height:
            return self.blocks[local_x][local_y]
        return AIR

    def set_block(self, local_x, local_y, block_id):
        """Ustaw blok w lokalnych współrzędnych."""
        if 0 <= local_x < self.width and 0 <= local_y < self.height:
            if self.blocks[local_x][local_y] != block_id:
                self.blocks[local_x][local_y] = block_id
                self.modified = True
            return True
        return False

    def save(self, world_path):
        """Zapisz chunk do pliku."""
        if not self.modified:
            return False
        chunk_file_path = os.path.join(world_path, 'chunks', f"chunk_{self.chunk_x}_{self.chunk_y}.dat")
        try:
            with open(chunk_file_path, 'wb') as f:
                pickle.dump(self.blocks, f)
            self.modified = False
            return True
        except Exception as e:
            print(f"Błąd zapisu chunka {self.chunk_x},{self.chunk_y}: {e}")
            return False

    def load(self, world_path):
        """Wczytaj chunk z pliku."""
        chunk_file_path = os.path.join(world_path, 'chunks', f"chunk_{self.chunk_x}_{self.chunk_y}.dat")
        if os.path.exists(chunk_file_path):
            try:
                with open(chunk_file_path, 'rb') as f:
                    self.blocks = pickle.load(f)
                    self.generated = True
                    self.modified = False
                return True
            except Exception as e:
                print(f"Błąd wczytania chunka {self.chunk_x},{self.chunk_y}: {e}")
                return False
        return False