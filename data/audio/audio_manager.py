import pygame
import os
from data.constants.constants import ASSET_DIR

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_enabled = True
        self.sound_enabled = True
        self.music_volume = 50
        self.sound_volume = 50
        self.sounds = {
            'click': self.load_sound('sfx/ui/click.wav'),
            'jump': self.load_sound('sfx/player/jump.wav'),
            'hurt': self.load_sound('sfx/player/hurt.wav'),
            'coin': self.load_sound('sfx/coin.wav'),
            'explosion': self.load_sound('sfx/explosion.wav'),
            'power_up': self.load_sound('sfx/power_up.wav'),
        }

    def load_sound(self, path):
        try:
            return pygame.mixer.Sound(os.path.join(ASSET_DIR, path))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Nie wczytano dźwięku {path}: {e}")
            return None

    def play_sound(self, sound_name):
        if self.sound_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(self.sound_volume / 100.0)
            self.sounds[sound_name].play()

    def play_music(self):
        if self.music_enabled:
            try:
                pygame.mixer.music.load(os.path.join(ASSET_DIR, 'bgm/main_theme.wav'))
                pygame.mixer.music.set_volume(self.music_volume / 100.0)
                pygame.mixer.music.play(-1)  # Zapętlanie muzyki
            except (pygame.error, FileNotFoundError) as e:
                print(f"Nie wczytano muzyki: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def toggle_music(self, state):
        self.music_enabled = state
        if self.music_enabled:
            self.play_music()  # Restartuj muzykę, jeśli włączona
        else:
            self.stop_music()

    def toggle_sound(self, state):
        self.sound_enabled = state

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume / 100.0)

    def set_sound_volume(self, volume):
        self.sound_volume = volume
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(volume / 100.0)