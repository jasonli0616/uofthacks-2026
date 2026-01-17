import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE

# Path to your background image (edit this to your filename)
BACKGROUND_PATH = "background.png"

# Fallback window size / color if image can't be loaded
FALLBACK_SIZE = (800, 600)
FALLBACK_BG_COLOR = (30, 30, 40)
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

    bg_image = load_background(BACKGROUND_PATH)
    if bg_image:
        window_size = bg_image.get_size()
    else:
        window_size = FALLBACK_SIZE

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Background Viewer")

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

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    try:
        sys.exit(0)
    except SystemExit:
        pass

if __name__ == "__main__":
    main()