import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, FULLSCREEN
from strings import StringSprite, START_POSITIONS
from start_screen import show_start_screen
from enemy_sprites import EnemySprite
from player_sprite import PlayerSprite
import random
import os


# Path to your background image (edit this to your filename)
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "imgs", "bg2.png")

# Fallback window size / color if image can't be loaded
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
FALLBACK_BG_COLOR = (82, 82, 82)
TARGET_FPS = 120

def load_background(path):
    try:
        image = pygame.image.load(BACKGROUND_PATH).convert_alpha()
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

    screen = pygame.display.set_mode(window_size, pygame.FULLSCREEN)
    pygame.display.set_caption("<Git />ar")
    bg_image = load_background(BACKGROUND_PATH)
    
    # Initialize pygame mixer for audio
    pygame.mixer.init()
    
    # Generate 25 notes based on the key
    notes_in_key = get_notes_in_key(config.scale)
    generated_notes = []
    strings = ["E", "A", "D", "G", "B", "e"]
    enemy_spawn_interval = 120  # Spawn every 2 seconds at 60 FPS
    
    for i in range(25):
        note_data = {
            'string': random.choice(strings),
            'note': random.choice(notes_in_key),
            'fret': random.randint(0, 12),
            'spawn_time': i * enemy_spawn_interval  # Stagger spawning
        }
        generated_notes.append(note_data)
    
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
    note_index = 0
   
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
        
        # Spawn enemies based on pre-generated notes
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_interval and note_index < len(generated_notes):
            enemy_spawn_timer = 0
            enemy_data = generated_notes[note_index]
            enemy = EnemySprite(enemy_data, speed=3)
            enemies_group.add(enemy)
            note_index += 1
        
        # Update and draw strings
        strings_group.update()
        strings_group.draw(screen)
        
        # Update and draw enemies
        enemies_group.update()
        enemies_group.draw(screen)
        # Draw trailing fret labels
        for enemy in enemies_group:
            if hasattr(enemy, "draw_label"):
                enemy.draw_label(screen)
        
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


def get_notes_in_key(scale):
    """Return notes that belong to the given scale/key."""
    # Major scales
    scales = {
        'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
        'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
        'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
        'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
        'B': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
        'F': ['F', 'G', 'A', 'A#', 'C', 'D', 'E'],
    }
    
    return scales.get(scale, ['C', 'D', 'E', 'F', 'G', 'A', 'B'])

if __name__ == "__main__":
    # Show start screen first
    config = show_start_screen()
    
    # If user didn't quit on start screen, run the main game
    if config:
        main(config)