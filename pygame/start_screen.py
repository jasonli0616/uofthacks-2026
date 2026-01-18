import pygame
import sys

# --- Configuration & Constants ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Palette - Marshall/Gibson inspired (Black, Gold, Red)
COLOR_BG_DARK = (10, 10, 12)       # Deep void black
COLOR_PANEL_BG = (25, 25, 28)      # Dark Grey for inputs
COLOR_DROPDOWN_BG = (20, 20, 22)   # Slightly darker for the list
COLOR_ACCENT = (200, 30, 30)       # Stage Light Red
COLOR_GOLD = (218, 165, 32)        # Vintage Gold
COLOR_TEXT_BRIGHT = (255, 255, 255)
COLOR_TEXT_DIM = (140, 140, 140)
COLOR_BORDER = (60, 60, 60)
COLOR_HOVER = (40, 40, 45)         # Lighter grey for hover states

# --- Classes ---

class GameConfig:
    def __init__(self):
        self.bpm = 120
        self.scale = "G Major / E Minor"
        self.instrument = "Shredding Guitar"
        self.genre = "Classic Rock"
        self.mood = "Crunchy Distortion"

class UIElement:
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.hovered = False

    def draw_label(self, surface, text, label_font):
        """Draws the label above the control"""
        shad = label_font.render(text.upper(), True, (0,0,0))
        surface.blit(shad, (self.rect.x + 1, self.rect.y - 24))
        lbl = label_font.render(text.upper(), True, COLOR_GOLD)
        surface.blit(lbl, (self.rect.x, self.rect.y - 25))

class Slider(UIElement):
    def __init__(self, x, y, w, h, label, min_val, max_val, font, label_font):
        super().__init__(x, y, w, h, font)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = 120
        self.label_font = label_font
        self.dragging = False

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.dragging = True
                self.update_value(mouse_pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(mouse_pos[0])

    def update_value(self, mouse_x):
        x = max(self.rect.x, min(mouse_x, self.rect.right))
        pct = (x - self.rect.x) / self.rect.width
        self.value = int(self.min_val + (pct * (self.max_val - self.min_val)))

    def draw(self, surface):
        self.draw_label(surface, f"{self.label}: {self.value}", self.label_font)

        # Track
        track_h = 6
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - track_h//2, self.rect.width, track_h)
        pygame.draw.rect(surface, (5, 5, 5), track_rect, border_radius=3)
        pygame.draw.rect(surface, (50, 50, 50), track_rect, 1, border_radius=3)

        # Active
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (pct * self.rect.width)
        active_rect = pygame.Rect(self.rect.x, self.rect.centery - track_h//2, handle_x - self.rect.x, track_h)
        pygame.draw.rect(surface, COLOR_ACCENT, active_rect, border_radius=3)

        # Cap
        cap_w = 14
        cap_h = 28
        cap_rect = pygame.Rect(handle_x - cap_w//2, self.rect.centery - cap_h//2, cap_w, cap_h)
        
        shadow_rect = cap_rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(surface, (0,0,0, 100), shadow_rect, border_radius=2)
        cap_col = (200, 200, 200) if self.hovered or self.dragging else (160, 160, 160)
        pygame.draw.rect(surface, cap_col, cap_rect, border_radius=2)
        pygame.draw.line(surface, (50, 50, 50), (cap_rect.centerx, cap_rect.top + 3), (cap_rect.centerx, cap_rect.bottom - 3), 2)


class Dropdown(UIElement):
    """A pop-out menu that smartly expands UP or DOWN"""
    def __init__(self, x, y, w, h, label, options, font, label_font):
        super().__init__(x, y, w, h, font)
        self.label = label
        self.options = options
        self.index = 0
        self.label_font = label_font
        self.is_open = False
        self.active_option_hover = -1 
        self.list_expands_up = False # Calculated dynamically

    def get_selected(self):
        return self.options[self.index]

    def _get_start_y_for_list(self):
        """Calculates where the list starts based on screen space"""
        total_h = len(self.options) * self.rect.height
        # If dropping down goes off screen (with 10px buffer), expand UP
        if self.rect.bottom + total_h > SCREEN_HEIGHT - 10:
            self.list_expands_up = True
            return self.rect.top - total_h
        else:
            self.list_expands_up = False
            return self.rect.bottom

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_open:
                start_y = self._get_start_y_for_list()
                clicked_option = False
                
                # Check clicks inside the expanded list
                for i, _ in enumerate(self.options):
                    opt_rect = pygame.Rect(self.rect.x, start_y + (i * self.rect.height), self.rect.width, self.rect.height)
                    if opt_rect.collidepoint(mouse_pos):
                        self.index = i
                        self.is_open = False
                        clicked_option = True
                        break
                
                # Close if clicked outside
                if not clicked_option and not self.rect.collidepoint(mouse_pos):
                    self.is_open = False
                elif self.rect.collidepoint(mouse_pos):
                     self.is_open = not self.is_open

            else:
                if self.rect.collidepoint(mouse_pos):
                    self.is_open = True

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.active_option_hover = -1
        if self.is_open:
             start_y = self._get_start_y_for_list()
             for i, _ in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, start_y + (i * self.rect.height), self.rect.width, self.rect.height)
                if opt_rect.collidepoint(mouse_pos):
                    self.active_option_hover = i

    def draw(self, surface):
        """Draws the main button (closed state)"""
        self.draw_label(surface, self.label, self.label_font)

        bg_col = COLOR_HOVER if self.is_open else COLOR_PANEL_BG
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=4)
        
        border_col = COLOR_ACCENT if (self.hovered or self.is_open) else COLOR_BORDER
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=4)

        # Arrow
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        if self.is_open:
            pygame.draw.polygon(surface, COLOR_GOLD, [(arrow_x-5, arrow_y+3), (arrow_x+5, arrow_y+3), (arrow_x, arrow_y-3)])
        else:
            pygame.draw.polygon(surface, COLOR_TEXT_DIM, [(arrow_x-5, arrow_y-3), (arrow_x+5, arrow_y-3), (arrow_x, arrow_y+3)])

        text = self.options[self.index]
        txt_surf = self.font.render(text, True, COLOR_TEXT_BRIGHT)
        surface.blit(txt_surf, (self.rect.x + 10, self.rect.centery - txt_surf.get_height()//2))

    def draw_list(self, surface):
        if not self.is_open:
            return

        total_h = len(self.options) * self.rect.height
        start_y = self._get_start_y_for_list()
        
        list_rect = pygame.Rect(self.rect.x, start_y, self.rect.width, total_h)
        
        # Shadow
        shadow_rect = list_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0,0,0, 150), shadow_rect, border_radius=4)

        # Background
        pygame.draw.rect(surface, COLOR_DROPDOWN_BG, list_rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDER, list_rect, 1, border_radius=4)

        for i, option in enumerate(self.options):
            opt_rect = pygame.Rect(self.rect.x, start_y + (i * self.rect.height), self.rect.width, self.rect.height)
            
            if i == self.active_option_hover:
                pygame.draw.rect(surface, COLOR_HOVER, opt_rect)
            
            if i == self.index:
                 pygame.draw.rect(surface, COLOR_GOLD, (opt_rect.x, opt_rect.y, 4, opt_rect.height))

            col = COLOR_GOLD if i == self.index else COLOR_TEXT_DIM
            if i == self.active_option_hover: col = COLOR_TEXT_BRIGHT
            
            txt_surf = self.font.render(option, True, col)
            surface.blit(txt_surf, (opt_rect.x + 15, opt_rect.centery - txt_surf.get_height()//2))
            
            if i < len(self.options) - 1:
                pygame.draw.line(surface, (40,40,40), (opt_rect.x, opt_rect.bottom-1), (opt_rect.right, opt_rect.bottom-1))


class BigButton(UIElement):
    def __init__(self, x, y, w, h, text, font):
        super().__init__(x, y, w, h, font)
        self.text = text

    def handle_event(self, event):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            return True
        return False

    def draw(self, surface):
        bg_col = (180, 20, 20) if self.hovered else (140, 10, 10)
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0,0,0), shadow_rect, border_radius=8)

        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_GOLD, self.rect, 2, border_radius=8)

        txt_surf = self.font.render(self.text.upper(), True, COLOR_TEXT_BRIGHT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

# --- Main Logic ---

def show_start_screen():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("<Git />ar - Setup")

    try:
        title_font = pygame.font.SysFont("impact", 80)
        ui_font = pygame.font.SysFont("arial", 20)
        label_font = pygame.font.SysFont("trebuchetms", 14, bold=True)
    except:
        title_font = pygame.font.Font(None, 80)
        ui_font = pygame.font.Font(None, 24)
        label_font = pygame.font.Font(None, 20)

    config = GameConfig()
    
    # Layout
    center_x = SCREEN_WIDTH // 2
    start_y = 250  
    gap = 75       
    input_w = 400
    input_h = 40
    left_align = center_x - (input_w // 2)

    # Data
    scale_opts = ["G Major / E Minor", "C Major / A Minor", "A Major / F# Minor", "D Major / B Minor", "E Major / C# Minor"]
    inst_opts = ["Shredding Guitar", "Precision Bass", "Warm Acoustic Guitar", "Dirty Synths", "Drumline"]
    genre_opts = ["Classic Rock", "Blues Rock", "60s Psychedelic Rock", "Funk Metal", "Surf Rock"]
    mood_opts = ["Crunchy Distortion", "Live Performance", "Psychedelic", "Saturated Tones", "Upbeat"]

    bpm_slider = Slider(left_align, start_y, input_w, input_h, "Tempo (BPM)", 90, 180, ui_font, label_font)
    
    dropdowns = [
        Dropdown(left_align, start_y + gap, input_w, input_h, "Key Scale", scale_opts, ui_font, label_font),
        Dropdown(left_align, start_y + gap*2, input_w, input_h, "Instrument", inst_opts, ui_font, label_font),
        Dropdown(left_align, start_y + gap*3, input_w, input_h, "Genre", genre_opts, ui_font, label_font),
        Dropdown(left_align, start_y + gap*4, input_w, input_h, "Vibe / Mood", mood_opts, ui_font, label_font)
    ]
    
    all_inputs = [bpm_slider] + dropdowns
    
    start_btn = BigButton(center_x - 100, SCREEN_HEIGHT - 90, 200, 50, "LET'S ROCK", ui_font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            active_dropdown = next((d for d in dropdowns if d.is_open), None)
            
            if active_dropdown:
                active_dropdown.handle_event(event)
                if active_dropdown.is_open and event.type == pygame.MOUSEBUTTONDOWN:
                    continue 

            if not active_dropdown:
                for i in all_inputs:
                    i.handle_event(event)
                
                if start_btn.handle_event(event):
                    config.bpm = bpm_slider.value
                    config.scale = dropdowns[0].get_selected()
                    config.instrument = dropdowns[1].get_selected()
                    config.genre = dropdowns[2].get_selected()
                    config.mood = dropdowns[3].get_selected()
                    running = False

        for d in dropdowns:
            d.update()

        screen.fill(COLOR_BG_DARK)
        
        # Spotlight
        center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        for r in range(500, 100, -20):
            pygame.draw.circle(surface=screen, color=(30, 30, 35), center=center_pos, radius=r, width=20)

        # Title
        t_shad = title_font.render("< GIT /> AR", True, (0,0,0))
        screen.blit(t_shad, (center_x - t_shad.get_width()//2 + 5, 65))
        t_main = title_font.render("< GIT /> AR", True, COLOR_TEXT_BRIGHT)
        screen.blit(t_main, (center_x - t_main.get_width()//2, 60))

        pygame.draw.line(screen, COLOR_BORDER, (center_x - 150, 150), (center_x + 150, 150), 1)

        bpm_slider.draw(screen)
        start_btn.draw(screen)
        for d in dropdowns:
            d.draw(screen)

        for d in dropdowns:
            if d.is_open:
                d.draw_list(screen)

        pygame.display.flip()
        clock.tick(60)

    return config

if __name__ == "__main__":
    conf = show_start_screen()
    print(f"\nLocked In: {conf.bpm} BPM | {conf.scale} | {conf.instrument}")
    pygame.quit()