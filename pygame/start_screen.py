import sys
import os
import pygame
import threading
import asyncio

from gemini.lyria import start_music_session

# --- CONFIGURATION ---
# Design resolution (the logic assumes this, then scales down/up)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# --- PATHS ---
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "imgs", "bg2.png")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "imgs", "title.png")

# Retro Palette (BIOS / Arcade Style)
COLOR_BG_DIM = (20, 20, 30)         # Dark Blue-Black
COLOR_FRAME_BORDER = (200, 200, 200) # Light Gray
COLOR_FRAME_FILL = (0, 0, 0)        # Black (The "Square" color)
COLOR_TEXT_LABEL = (100, 200, 255)  # Cyan
COLOR_TEXT_VALUE = (255, 255, 0)    # Yellow (Retro Highlight)
COLOR_CURSOR = (255, 255, 255)      # White

def ensure_placeholder_logo(path, text="<Git />ar", size=(600, 160), font_size=96):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        return
    if not pygame.get_init(): pygame.init()
    if not pygame.font.get_init(): pygame.font.init()
    
    surf = pygame.Surface(size, pygame.SRCALPHA)
    font = pygame.font.SysFont("consolas", font_size, bold=True)
    if not font: font = pygame.font.SysFont(None, font_size)
    
    # Retro drop shadow style
    shadow = font.render(text, True, (0, 0, 80))
    main = font.render(text, True, (255, 255, 255))
    
    rect = surf.get_rect()
    surf.blit(shadow, (rect.centerx - main.get_width()//2 + 6, rect.centery - main.get_height()//2 + 6))
    surf.blit(main,   (rect.centerx - main.get_width()//2,     rect.centery - main.get_height()//2))
    
    try: pygame.image.save(surf, path)
    except: pass

class StartScreen:
    def __init__(self, screen, bg_image=None, scale=1.0, offset=(0,0)):
        self.screen = screen
        self.scale = max(0.0001, float(scale))
        self.offset = offset
        self.clock = pygame.time.Clock()

        # Handle Background Loading internally if not provided
        if bg_image is None:
            try:
                self.bg_image = pygame.image.load(BACKGROUND_PATH).convert()
            except:
                self.bg_image = None
        else:
            self.bg_image = bg_image

        # Load standard fonts
        font_names = pygame.font.get_fonts()
        retro_font = 'couriernew' if 'couriernew' in font_names else None
        
        # Scaling fonts
        self.font_header = pygame.font.SysFont(retro_font, int(55 * self.scale), bold=True)
        self.font_label = pygame.font.SysFont(retro_font, int(28 * self.scale), bold=True)
        self.font_input = pygame.font.SysFont(retro_font, int(38 * self.scale))
        self.font_btn = pygame.font.SysFont(retro_font, int(42 * self.scale), bold=True)

        ensure_placeholder_logo(LOGO_PATH)
        try: self.logo_image = pygame.image.load(LOGO_PATH).convert_alpha()
        except: self.logo_image = None

        # --- THE IDENTITY FORM ---
        self.inputs = [
            # CHANGED: "CLASS" -> "WEAPON" to fit the shooting gameplay
            {"label": "WEAPON (INSTRUMENT)", "text": "Acoustic Guitar", "key": "instrument"},
            {"label": "ORIGIN (GENRE)",      "text": "Classic Rock",    "key": "genre"},
            {"label": "SPIRIT (MOOD)",       "text": "Relaxed",         "key": "mood"},
        ]
        self.active_idx = None

    def draw_retro_box(self, rect, border_width=4):
        """Draws a 'BIOS' style text box."""
        # 1. Fill with Opaque Black
        pygame.draw.rect(self.screen, COLOR_FRAME_FILL, rect) 
        # 2. Draw Borders
        pygame.draw.rect(self.screen, COLOR_FRAME_BORDER, rect, int(border_width * self.scale)) 
        # Double border effect
        inner_rect = rect.inflate(-8*self.scale, -8*self.scale)
        pygame.draw.rect(self.screen, COLOR_FRAME_BORDER, inner_rect, max(1, int(2 * self.scale)))

    def draw(self):
        w, h = self.screen.get_size()
        cx, cy = w // 2, h // 2

        # 1. Background
        if self.bg_image:
            scaled_bg = pygame.transform.scale(self.bg_image, (w, h))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            self.screen.fill(COLOR_BG_DIM)

        # 2. Main Frame (Centered Black Box)
        box_w = int(950 * self.scale)
        box_h = int(800 * self.scale)
        box_rect = pygame.Rect(0, 0, box_w, box_h)
        vertical_shift = int(20 * self.scale)
        box_rect.center = (cx, cy - vertical_shift)
        
        self.draw_retro_box(box_rect)

        # 3. Logo / Title
        content_top_y = box_rect.top + int(60 * self.scale)
        
        if self.logo_image:
            logo_target_w = int(300 * self.scale) 
            ratio = logo_target_w / self.logo_image.get_width()
            logo_h = int(self.logo_image.get_height() * ratio)
            scaled_logo = pygame.transform.smoothscale(self.logo_image, (logo_target_w, logo_h))
            logo_rect = scaled_logo.get_rect(midtop=(cx, content_top_y))
            self.screen.blit(scaled_logo, logo_rect)
            
            # Gap after logo
            current_y = logo_rect.bottom + int(20 * self.scale) 
        else:
            title_surf = self.font_header.render("IDENTITY SETUP", True, (255, 255, 255))
            title_rect = title_surf.get_rect(midtop=(cx, content_top_y))
            self.screen.blit(title_surf, title_rect)
            current_y = title_rect.bottom + int(20 * self.scale)

        # 4. Inputs
        field_spacing = int(110 * self.scale) 
        input_width = int(650 * self.scale)
        input_height = int(55 * self.scale)

        for i, fld in enumerate(self.inputs):
            label_surf = self.font_label.render(fld["label"], True, COLOR_TEXT_LABEL)
            label_rect = label_surf.get_rect(midtop=(cx, current_y))
            self.screen.blit(label_surf, label_rect)

            current_y += int(35 * self.scale)
            
            input_rect = pygame.Rect(0, 0, input_width, input_height)
            input_rect.midtop = (cx, current_y)
            fld["rect"] = input_rect 
            
            is_active = (i == self.active_idx)
            # Input box background
            bg_col = (20, 20, 20) if not is_active else (0, 0, 0)
            pygame.draw.rect(self.screen, bg_col, input_rect)
            pygame.draw.rect(self.screen, COLOR_TEXT_LABEL, input_rect, max(1, int(3*self.scale)))

            txt_surf = self.font_input.render(fld["text"], True, COLOR_TEXT_VALUE)
            txt_rect = txt_surf.get_rect(center=input_rect.center)
            self.screen.blit(txt_surf, txt_rect)

            if is_active and (pygame.time.get_ticks() // 500) % 2 == 0:
                cursor_x = txt_rect.right + int(5 * self.scale)
                cursor_h = int(30 * self.scale)
                pygame.draw.rect(self.screen, COLOR_CURSOR, (cursor_x, input_rect.centery - cursor_h//2, int(10*self.scale), cursor_h))

            current_y += field_spacing

        # 5. Start Button
        btn_w = int(250 * self.scale)
        btn_h = int(65 * self.scale)
        self.btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
        
        # CHANGED: Pushed down by 10px (Offset changed from -50 to -40)
        button_y_pos = current_y - int(40 * self.scale) 
        self.btn_rect.midtop = (cx, button_y_pos)
        
        mouse_pos = pygame.mouse.get_pos()
        hover = self.btn_rect.collidepoint(mouse_pos)
        
        btn_col = (255, 0, 0) if hover else (180, 0, 0)
        pygame.draw.rect(self.screen, btn_col, self.btn_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.btn_rect, max(1, int(3*self.scale)))
        
        btn_txt = self.font_btn.render("START", True, (255, 255, 255))
        btn_txt_rect = btn_txt.get_rect(center=self.btn_rect.center)
        self.screen.blit(btn_txt, btn_txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            self.active_idx = None
            
            for i, fld in enumerate(self.inputs):
                if fld["rect"].collidepoint(pos):
                    self.active_idx = i
                    return None
            
            if self.btn_rect.collidepoint(pos):
                cfg = self._build_config()
                self._launch_music(cfg)
                return cfg

        if event.type == pygame.KEYDOWN:
            if self.active_idx is not None:
                fld = self.inputs[self.active_idx]
                if event.key == pygame.K_BACKSPACE:
                    fld["text"] = fld["text"][:-1]
                elif event.key == pygame.K_RETURN:
                    if self.active_idx < len(self.inputs) - 1:
                        self.active_idx += 1
                    else:
                        cfg = self._build_config()
                        self._launch_music(cfg)
                        return cfg
                elif event.key == pygame.K_TAB:
                    self.active_idx = (self.active_idx + 1) % len(self.inputs)
                else:
                    if event.unicode.isprintable():
                        fld["text"] += event.unicode
        return None

    def _launch_music(self, cfg):
        print(f"Identity Confirmed: {cfg.instrument} | {cfg.genre} | {cfg.mood}")
        def run_music_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(start_music_session(
                    instrument=cfg.instrument, genre=cfg.genre, mood=cfg.mood, bpm=cfg.bpm
                ))
            except Exception as e: print(f"Music Error: {e}")
            finally: loop.close()
        threading.Thread(target=run_music_loop, daemon=True).start()

    def _build_config(self):
        class Config: pass
        cfg = Config()
        cfg.bpm = 120
        cfg.scale = "G_MAJOR_E_MINOR"
        cfg.instrument = self.inputs[0]["text"].strip() or "Electric Guitar"
        cfg.genre      = self.inputs[1]["text"].strip() or "Rock"
        cfg.mood       = self.inputs[2]["text"].strip() or "Energetic"
        return cfg

    def run(self):
        pygame.key.set_repeat(400, 50)
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: return None
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return None
                    res = self.handle_event(event)
                    if res: return res
                self.draw()
                pygame.display.flip()
                self.clock.tick(60)
        finally:
            pygame.key.set_repeat(0)

if __name__ == "__main__":
    pygame.init(); pygame.font.init()
    s = pygame.display.set_mode((1280, 720)) # Test resolution
    StartScreen(s, None, scale=1280/1920).run()
    pygame.quit()