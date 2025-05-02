import pygame
import sys
import os
import json
import hashlib
from data.game import Game
from data.constants.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Funkcja obliczająca SHA1 pliku
def get_file_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

# Funkcja sprawdzająca czy wszystkie niezbędne pliki assets istnieją i mają poprawne sumy SHA1
def verify_assets():
    assets_json_path = 'data/assets.json'
    if not os.path.exists(assets_json_path):
        print("Weryfikacja assets zakończona błędem: brak pliku")
        return False

    with open(assets_json_path, 'r', encoding='utf-8') as f:
        assets_data = json.load(f)

    # Weryfikacja, czy wszystkie pliki istnieją i mają poprawne sumy SHA1
    all_ok = True
    for asset in assets_data:
        folder = asset['dir'].replace('assets/', '')
        file = asset['file']
        expected_sha1 = asset['sha1']
        
        full_path = os.path.join("assets", folder, file)
        if not os.path.exists(full_path):
            all_ok = False
            print(f"Brakuje pliku: {file} (w folderze {folder})")
        else:
            # Obliczamy SHA1 pliku
            actual_sha1 = get_file_sha1(full_path)
            if actual_sha1 != expected_sha1:
                all_ok = False
                print(f"Plik {file} (w folderze {folder}) ma nieprawidłową sumę SHA1. Oczekiwana: {expected_sha1}, obliczona: {actual_sha1}")

    if all_ok:
        print("Weryfikacja assets udana")

    return all_ok

# Główna funkcja gry
def main():
    # Sprawdzenie, czy plik assets.json istnieje i jest poprawny
    if not verify_assets():
        print("Nie wszystkie potrzebne pliki zostały znalezione. Gra nie może zostać uruchomiona.")
        sys.exit(1)

    # Inicjalizacja Pygame
    pygame.init()

    # Ustawienie rozdzielczości okna gry
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sandbox 2D")

    # Tworzymy foldery jeśli nie istnieją (np. na logi i światy)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    if not os.path.exists('worlds'):
        os.makedirs('worlds')

    # Inicjalizacja obiektu Game
    game = Game()

    # Uruchomienie głównej pętli gry z game.py
    game.run()


# Start programu
if __name__ == "__main__":
    main()
