import sys
import os
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE

from start_screen import StartScreen, window_size, FALLBACK_BG_COLOR, SCREEN_WIDTH as DESIGN_WIDTH, SCREEN_HEIGHT as DESIGN_HEIGHT
from strings import StringSprite, START_POSITIONS
from enemy_sprites import EnemySprite
from player_sprite import PlayerSprite

# Path to your background image
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "imgs", "bg2.png")

TARGET_FPS = 120

def load_background(path):
	# ...existing code...
	try:
		image = pygame.image.load(path).convert_alpha()
		image = image.convert()
		return image
	except Exception as e:
		print(f"Warning: could not load background '{path}': {e}", file=sys.stderr)
		return None

def get_notes_in_key(scale):
	# ...existing code...
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

def main(config=None):
	# ...existing code...
	pygame.init()
	clock = pygame.time.Clock()

	# Create a fixed window at 1280x720 (no fullscreen)
	SCREEN_W, SCREEN_H = 1280, 720
	screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
	pygame.display.set_caption("<Git />ar")

	# Compute runtime scaling so the game layout (designed for DESIGN_WIDTH x DESIGN_HEIGHT)
	# scales uniformly and is letterboxed/centered inside the fixed window.
	screen_w, screen_h = screen.get_size()
	scale = min(screen_w / DESIGN_WIDTH, screen_h / DESIGN_HEIGHT)
	offset_x = int((screen_w - DESIGN_WIDTH * scale) / 2)
	offset_y = int((screen_h - DESIGN_HEIGHT * scale) / 2)
	offset = (offset_x, offset_y)

	bg_image = load_background(BACKGROUND_PATH)

	# Show start screen and get config from the UI; pass scale+offset so UI is scaled
	start_screen = StartScreen(screen, bg_image, scale=scale, offset=offset)
	cfg = start_screen.run()
	if cfg is None:
		pygame.quit()
		try:
			sys.exit(0)
		except SystemExit:
			pass
		return

	config = cfg

	# Initialize mixer after leaving start screen
	pygame.mixer.init()

	notes_in_key = get_notes_in_key(config.scale)
	generated_notes = []
	strings = ["E", "A", "D", "G", "B", "e"]
	enemy_spawn_interval = 120

	for i in range(25):
		note_data = {
			'string': random.choice(strings),
			'note': random.choice(notes_in_key),
			'fret': random.randint(0, 12),
			'spawn_time': i * enemy_spawn_interval
		}
		generated_notes.append(note_data)

	# Create sprite group for guitar strings (pass scale+offset so sprites position/size correctly)
	strings_group = pygame.sprite.Group()
	for position, note in START_POSITIONS.items():
		string_sprite = StringSprite(note, position, scale=scale, offset=offset)
		strings_group.add(string_sprite)

	# Create sprite group for enemies
	enemies_group = pygame.sprite.Group()

	# Create player sprite
	player = PlayerSprite(scale=scale, offset=offset)
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
			# Scale background to fill letterboxed area (we keep aspect via scale, then blit centered)
			bg_scaled = pygame.transform.smoothscale(bg_image, (int(DESIGN_WIDTH * scale), int(DESIGN_HEIGHT * scale)))
			screen.fill((0, 0, 0))  # clear with black for letterbox borders
			screen.blit(bg_scaled, (offset_x, offset_y))
		else:
			screen.fill(FALLBACK_BG_COLOR)

		# Spawn enemies based on pre-generated notes (pass actual screen width so spawn is at visible edge)
		enemy_spawn_timer += 1
		if enemy_spawn_timer >= enemy_spawn_interval and note_index < len(generated_notes):
			enemy_spawn_timer = 0
			enemy_data = generated_notes[note_index]
			enemy = EnemySprite(enemy_data, speed=3, screen_width=screen_w, scale=scale, offset=offset)
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