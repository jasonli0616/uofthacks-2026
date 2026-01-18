import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from strings import StringSprite, START_POSITIONS
from start_screen import show_start_screen
from enemy_sprites import EnemySprite
from player_sprite import PlayerSprite
import random
import os


# Path to your background image (edit this to your filename)
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "imgs", "background.png")

# Fallback window size / color if image can't be loaded
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
FALLBACK_BG_COLOR = (82, 82, 82)
TARGET_FPS = 60

def load_background(path):
    try:
        image = pygame.image.load(path)
        # convert for faster blitting; use convert_alpha() if you need per-pixel alpha
        image = image.convert()
        return image
    except Exception as e:
        # Failed to load image; caller will handle fallback
        print(f"Warning: could not load background '{path}': {e}", file=sys.stderr)
        return None

def main(config):
    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("<Git />ar")
    bg_image = load_background(BACKGROUND_PATH)
    
    # Game config is available here if needed
    # config.bpm, config.scale, config.main_instrument, config.main_genre, config.mood
    
    # Create sprite group for guitar strings
    strings_group = pygame.sprite.Group()
    for position, note in START_POSITIONS.items():
        string_sprite = StringSprite(note, position)
        strings_group.add(string_sprite)
    
    # Create sprite group for enemies
    enemies_group = pygame.sprite.Group()
    
    # Create player sprite
    player = PlayerSprite()
    player_group = pygame.sprite.Group()
    player_group.add(player)
    
    # Enemy spawn timer
    enemy_spawn_timer = 0
    enemy_spawn_interval = 120  # Spawn every 2 seconds at 60 FPS
   
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(FALLBACK_BG_COLOR)
        
        # Spawn enemies periodically
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemy_spawn_timer = 0
            # Spawn an enemy on a random string with random note and fret
            strings = ["E", "A", "D", "G", "B", "e"]
            notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
            enemy_data = {
                'string': random.choice(strings),
                'note': random.choice(notes),
                'fret': random.randint(0, 12)
            }
            enemy = EnemySprite(enemy_data, speed=3)
            enemies_group.add(enemy)
        
        # Update and draw strings
        strings_group.update()
        strings_group.draw(screen)
        
        # Update and draw enemies
        enemies_group.update()
        enemies_group.draw(screen)
        
        # Update and draw player
        player_group.update()
        player_group.draw(screen)
        
        # Remove enemies that are off screen
        for enemy in enemies_group:
            if enemy.rect.right < 0:
                enemy.kill()

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    try:
        sys.exit(0)
    except SystemExit:
        pass

if __name__ == "__main__":
    # Show start screen first
    config = show_start_screen()
    
    # If user didn't quit on start screen, run the main game
    if config:
        main(config)