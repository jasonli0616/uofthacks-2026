import sys
import os
import pygame

# Display constants used by start screen and imported by game.py
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
FALLBACK_BG_COLOR = (82, 82, 82)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "imgs", "title.png")

def ensure_placeholder_logo(path, text="<Git />ar", size=(600, 160), font_size=96):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	if os.path.exists(path):
		return
	if not pygame.get_init():
		pygame.init()
	if not pygame.font.get_init():
		pygame.font.init()
	surf = pygame.Surface(size, pygame.SRCALPHA)
	surf.fill((0, 0, 0, 0))
	box_rect = surf.get_rect().inflate(-10, -10)
	pygame.draw.rect(surf, (30, 30, 30), box_rect, border_radius=12)
	font = pygame.font.SysFont(None, font_size)
	txt = font.render(text, True, (230, 230, 230))
	txt_rect = txt.get_rect(center=surf.get_rect().center)
	surf.blit(txt, txt_rect)
	try:
		pygame.image.save(surf, path)
	except Exception as e:
		print(f"Warning: could not save placeholder logo '{path}': {e}", file=sys.stderr)

class StartScreen:
	def __init__(self, screen, bg_image, scale=1.0, offset=(0,0)):
		self.screen = screen
		self.bg_image = bg_image
		self.scale = max(0.0001, float(scale))
		self.offset = offset
		# scale fonts but ensure a reasonable min size
		self.font = pygame.font.SysFont(None, max(12, int(36 * self.scale)))
		self.title_font = pygame.font.SysFont(None, max(18, int(72 * self.scale)))
		self.clock = pygame.time.Clock()

		ensure_placeholder_logo(LOGO_PATH, text="<Git />ar")
		try:
			self.logo_image = pygame.image.load(LOGO_PATH).convert_alpha()
		except Exception:
			self.logo_image = None

		# Reduce logo target size by half so it doesn't push UI off-screen
		self.logo_scale_factor = 0.5

		# Small vertical shift (in design-space scaled units) to move inputs down under the logo
		self.v_shift = int(60 * self.scale)

		# Input fields configuration -- positions are in design-space; scale & offset them
		def s_rect(x, y, w, h):
			return pygame.Rect(int(x * self.scale + self.offset[0]),
							   int((y + self.v_shift / self.scale) * self.scale + self.offset[1]),
							   max(1, int(w * self.scale)),
							   max(1, int(h * self.scale)))

		self.inputs = [
			{"label": "Backing instrument", "text": "", "rect": s_rect(560, 380, 800, 40)},
			{"label": "Genre",              "text": "", "rect": s_rect(560, 450, 800, 40)},
			{"label": "Mood",               "text": "", "rect": s_rect(560, 520, 800, 40)},
		]
		self.active_idx = None
		self.begin_rect = s_rect(860, 600, 200, 50)

	def draw_placeholder_background(self):
		# Draw fallback solid background and a large "BACKGROUND" label for placeholder
		self.screen.fill(FALLBACK_BG_COLOR)
		big = self.title_font.render("BACKGROUND", True, (200, 200, 200))
		# center in design-space then convert to screen coords (apply v_shift)
		center_x = int((SCREEN_WIDTH // 2) * self.scale + self.offset[0])
		center_y = int((SCREEN_HEIGHT // 3) * self.scale + self.offset[1] + self.v_shift)
		br = big.get_rect(center=(center_x, center_y))
		self.screen.blit(big, br)

	def draw(self):
		# draw background image or placeholder
		if self.bg_image:
			self.screen.blit(pygame.transform.scale(self.bg_image, (int(SCREEN_WIDTH * self.scale), int(SCREEN_HEIGHT * self.scale))), (self.offset[0], self.offset[1]))
		else:
			self.draw_placeholder_background()

		# Draw logo (if loaded) above the title
		if self.logo_image:
			# Make logo half the previous target size so it fits reliably
			target_w = int(800 * self.scale * self.logo_scale_factor)
			logo_w = min(target_w, self.logo_image.get_width())
			scale_ratio = logo_w / max(1, self.logo_image.get_width())
			logo_h = int(self.logo_image.get_height() * scale_ratio)
			logo_surf = pygame.transform.smoothscale(self.logo_image, (logo_w, logo_h))
			# Position logo so its bottom is just above the first input field (small scaled margin)
			center_x = int((SCREEN_WIDTH // 2) * self.scale + self.offset[0])
			margin = int(8 * self.scale)
			# midbottom places the logo's bottom at (x, y); subtract margin from the top of first input
			logo_rect = logo_surf.get_rect(midbottom=(center_x, self.inputs[0]["rect"].top - margin))
			self.screen.blit(logo_surf, logo_rect)

		# Draw input fields
		for i, fld in enumerate(self.inputs):
			# label
			lbl = self.font.render(fld["label"], True, (220, 220, 220))
			self.screen.blit(lbl, (fld["rect"].x, fld["rect"].y - int(28 * self.scale)))

			# box background
			color = (255, 255, 255) if i == self.active_idx else (200, 200, 200)
			pygame.draw.rect(self.screen, (30, 30, 30), fld["rect"])
			pygame.draw.rect(self.screen, color, fld["rect"], max(1, int(2 * self.scale)))

			# text
			text_surf = self.font.render(fld["text"], True, (255, 255, 255))
			text_pos = (fld["rect"].x + int(8 * self.scale), fld["rect"].y + int(6 * self.scale))
			self.screen.blit(text_surf, text_pos)

			# Draw blinking caret if this field is active
			if i == self.active_idx:
				blink_on = (pygame.time.get_ticks() // 500) % 2 == 0
				if blink_on:
					txt_w = text_surf.get_width()
					caret_x = fld["rect"].x + int(8 * self.scale) + txt_w + int(2 * self.scale)
					caret_y = fld["rect"].y + int(8 * self.scale)
					caret_h = max(4, self.font.get_height() - int(4 * self.scale))
					caret_rect = pygame.Rect(caret_x, caret_y, max(1, int(2 * self.scale)), caret_h)
					pygame.draw.rect(self.screen, (255, 255, 255), caret_rect)

		# Begin button
		pygame.draw.rect(self.screen, (50, 150, 50), self.begin_rect)
		btn_text = self.font.render("Begin Game", True, (255, 255, 255))
		btn_rect = btn_text.get_rect(center=self.begin_rect.center)
		self.screen.blit(btn_text, btn_rect)

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			pos = event.pos
			# Check inputs
			self.active_idx = None
			for i, fld in enumerate(self.inputs):
				if fld["rect"].collidepoint(pos):
					self.active_idx = i
					return None
			# Check begin button
			if self.begin_rect.collidepoint(pos):
				# Build config from inputs and return
				cfg = self._build_config()
				return cfg

		if event.type == pygame.KEYDOWN:
			if self.active_idx is not None:
				fld = self.inputs[self.active_idx]
				if event.key == pygame.K_BACKSPACE:
					fld["text"] = fld["text"][:-1]
				elif event.key == pygame.K_RETURN:
					# Move focus to next input or submit
					if self.active_idx < len(self.inputs) - 1:
						self.active_idx += 1
					else:
						return self._build_config()
				else:
					# Append printable characters
					ch = event.unicode
					if ch.isprintable():
						fld["text"] += ch
		return None

	def _build_config(self):
		class Config:
			pass
		cfg = Config()
		cfg.bpm = 120
		cfg.scale = "G"  # keep default scale for now
		cfg.instrument = self.inputs[0]["text"] or "Backing Guitar"
		cfg.genre = self.inputs[1]["text"] or "Rock"
		cfg.mood = self.inputs[2]["text"] or "Neutral"
		cfg.instrument = cfg.instrument.strip()
		cfg.genre = cfg.genre.strip()
		cfg.mood = cfg.mood.strip()
		return cfg

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					return None
				result = self.handle_event(event)
				if result is not None:
					return result

			self.draw()
			pygame.display.flip()
			self.clock.tick(60)