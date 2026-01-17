import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from strings import StringSprite, START_POSITIONS

# Path to your background image (edit this to your filename)
BACKGROUND_PATH = "background.png"

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

def main():
    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("<Git />ar")
    bg_image = load_background(BACKGROUND_PATH)
    
    # Create sprite group for guitar strings
    strings_group = pygame.sprite.Group()
    for position, note in START_POSITIONS.items():
        string_sprite = StringSprite(note, position)
        strings_group.add(string_sprite)
   
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
        
        # Update and draw strings
        strings_group.update()
        strings_group.draw(screen)

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    try:
        sys.exit(0)
    except SystemExit:
        pass

if __name__ == "__main__":
    main()