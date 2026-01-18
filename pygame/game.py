import sys
import os
import pygame
import threading
import time
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN

from start_screen import StartScreen, SCREEN_WIDTH as DESIGN_WIDTH, SCREEN_HEIGHT as DESIGN_HEIGHT
from strings import StringSprite, START_POSITIONS
from enemy_sprites import EnemySprite
from player_sprite import PlayerSprite
from gemini.enemies import generate_musical_track  
import audio


audio.start_audio_stream()
# Import the new Polling Listener
import guitar_listener 

# --- CONFIGURATION ---
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "imgs", "bg2.png")
HEART_PATH = os.path.join(os.path.dirname(__file__), "imgs", "heart.png")
TARGET_FPS = 60
FALLBACK_BG_COLOR = (20, 20, 20)

# --- NOTE LOGIC ---
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
STRING_OFFSETS = {'E': 4, 'A': 9, 'D': 14, 'G': 19, 'B': 23, 'e': 28}

def get_enemy_note_name(enemy):
    """
    Calculates the note name (e.g., 'C') based on string+fret.
    Does NOT include octave for gameplay simplicity, but you can add it if needed.
    """
    try:
        base_val = STRING_OFFSETS.get(enemy.string, 0)
        note_index = (base_val + enemy.fret) % 12
        return NOTE_NAMES[note_index]
    except:
        return None

def load_background(path):
    try:
        image = pygame.image.load(path).convert_alpha()
        return image.convert()
    except: return None

def restart_game():
    print("Restarting...")
    guitar_listener.stop_audio_stream()
    pygame.quit()
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    pygame.init()
    try: pygame.mixer.init()
    except: pass
    clock = pygame.time.Clock()

    SCREEN_W, SCREEN_H = 1280, 720
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("<Git />ar")

    screen_w, screen_h = screen.get_size()
    scale = min(screen_w / DESIGN_WIDTH, screen_h / DESIGN_HEIGHT)
    offset_x = int((screen_w - DESIGN_WIDTH * scale) / 2)
    offset_y = int((screen_h - DESIGN_HEIGHT * scale) / 2)
    offset = (offset_x, offset_y)

    barrier_screen_x = offset_x + int(370 * scale) 
    play_area_x = offset_x + int(200 * scale)      

    bg_image = load_background(BACKGROUND_PATH)
    heart_img = None
    try:
        heart_img = pygame.image.load(HEART_PATH).convert_alpha()
        heart_img = pygame.transform.smoothscale(heart_img, (30, 30))
    except: pass

    # START SCREEN
    start_screen = StartScreen(screen, bg_image, scale=scale, offset=offset)
    config = start_screen.run()
    if config is None: pygame.quit(); sys.exit()

    # GENERATION
    generation_result = {"notes": []}
    def generator():
        try:
            generation_result["notes"] = generate_musical_track(config.scale, config.bpm, 120) or []
        except: generation_result["notes"] = []
    threading.Thread(target=generator, daemon=True).start()

    # LOADING
    font_loading = pygame.font.SysFont(None, 60)
    loading_start = pygame.time.get_ticks()
    while True:
        
        if pygame.time.get_ticks() - loading_start > 4000 and generation_result["notes"]: break
        for e in pygame.event.get():
            if e.type == QUIT: pygame.quit(); sys.exit()
        screen.fill((20, 20, 20))
        txt = font_loading.render("TUNING GUITARS...", True, (200, 200, 200))
        screen.blit(txt, txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
        pygame.display.flip()
        clock.tick(60)

    generated_notes = generation_result["notes"]

    # SPRITES
    strings_group = pygame.sprite.Group()
    for position, note in START_POSITIONS.items():
        strings_group.add(StringSprite(note, position, scale=scale, offset=offset))

    enemies_group = pygame.sprite.Group()
    beam_group = pygame.sprite.Group()
    player = PlayerSprite(scale=scale, offset=offset)
    player_group = pygame.sprite.Group()
    player_group.add(player)

    # --- START AUDIO ---
    guitar_listener.start_audio_stream()

    max_health = 5
    current_health = max_health
    game_tick_counter = 0
    note_index = 0
    game_over = False
    
    last_damage_time = 0
    damage_cooldown_ms = 1000 
    
    # Cooldown for shooting (prevents one pluck killing 5 enemies instantly)
    last_shot_time = 0
    shot_cooldown = 0.2

    font_go = pygame.font.SysFont(None, 120)
    font_btn = pygame.font.SysFont(None, 60)

    running = True
    while running:
        current_time = pygame.time.get_ticks() / 1000.0 # seconds


        for event in pygame.event.get():
            if event.type == QUIT: running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE: running = False
            if game_over and event.type == MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if pygame.Rect(SCREEN_W//2 - 150, SCREEN_H//2 + 50, 300, 80).collidepoint(mx, my):
                    restart_game()

        # --- POLLING AUDIO LOGIC ---
        if not game_over:
            
            # 1. Get current pitch (e.g. "A2")
            detected_pitch = audio.get_pitch()  # returns note string or None
           
            
            if detected_pitch and (current_time - last_shot_time > shot_cooldown):
                # Strip the octave number for game comparison (e.g. "A2" -> "A")
                # If you want strict octave matching, remove this line.
                note_name = detected_pitch[:-1] 

                # 2. Find Targets
                targets = [
                    e for e in enemies_group 
                    if e.rect.centerx <= barrier_screen_x and e.rect.right > 0
                ]
                
                # 3. Match Note
                hit_enemy = None
                for e in targets:
                    if get_enemy_note_name(e) == note_name:
                        hit_enemy = e
                        break # Only shoot one at a time
                
                if hit_enemy:
                    print(f"Shot {note_name} (from {detected_pitch})")
                    beam = player.shoot_particle_beam(note_name, target_enemy=hit_enemy)
                    if beam: beam_group.add(beam)
                    last_shot_time = current_time

            # GAME UPDATE
            game_tick_counter += 1
            while note_index < len(generated_notes):
                next_note = generated_notes[note_index]
                if game_tick_counter >= next_note['spawn_time']:
                    enemies_group.add(EnemySprite(next_note, speed=3, screen_width=SCREEN_W, scale=scale, offset=offset))
                    note_index += 1
                else: break

            strings_group.update(); enemies_group.update()
            player_group.update(); beam_group.update()

            # DAMAGE CHECK
            current_ms = pygame.time.get_ticks()
            for enemy in list(enemies_group):
                if enemy.rect.right < play_area_x:
                    enemy.kill() 
                    if current_ms - last_damage_time > damage_cooldown_ms:
                        current_health -= 1
                        last_damage_time = current_ms
            
            if current_health <= 0: game_over = True

        # DRAWING
        if bg_image: screen.blit(pygame.transform.smoothscale(bg_image, (int(DESIGN_WIDTH*scale), int(DESIGN_HEIGHT*scale))), offset)
        else: screen.fill(FALLBACK_BG_COLOR)

        pygame.draw.line(screen, (255, 0, 0), (barrier_screen_x, 0), (barrier_screen_x, SCREEN_H), 2)
        
        strings_group.draw(screen); enemies_group.draw(screen)
        for e in enemies_group: 
            if hasattr(e, "draw_label"): e.draw_label(screen)
        player_group.draw(screen); beam_group.draw(screen)

        if heart_img:
            for i in range(current_health): screen.blit(heart_img, ((SCREEN_W - 50) - (i * 40), 20))

        if game_over:
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA); s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            txt = font_go.render("GAME OVER", True, (255, 50, 50))
            screen.blit(txt, txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 50)))
            pygame.draw.rect(screen, (50, 200, 50), (SCREEN_W//2 - 150, SCREEN_H//2 + 50, 300, 80), border_radius=12)
            btn = font_btn.render("RESTART", True, (255, 255, 255))
            screen.blit(btn, btn.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 90)))

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    guitar_listener.stop_audio_stream()
    pygame.quit()

if __name__ == "__main__":
    main()