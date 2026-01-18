import os
import json
import random
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

def generate_musical_track(scale_name, bpm=120, duration_seconds=60):
    """
    Generates a list of enemy spawn data.
    STRATEGY: Use Gemini for melodic PITCH (string/fret), but strictly control RHYTHM via code.
    """
    
    # Game runs at ~120 FPS. 
    ticks_per_beat = (120 * 60) / bpm 

    api_key = os.environ.get("GOOGLE_API_KEY")
    
    # 1. GET MELODY FROM GEMINI
    melody_data = []
    
    if api_key:
        try:
            print(f"Contacting Gemini for melody ({scale_name})...")
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            Write a list of guitar notes for a solo in {scale_name}.
            Return 40-50 notes. 
            Single notes only. Frets 0-12.
            
            Return ONLY JSON:
            [
                {{"string": "E", "fret": 0}},
                {{"string": "A", "fret": 2}}
            ]
            """

            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            text = response.text
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                melody_data = json.loads(text[start_idx:end_idx])

        except Exception as e:
            print(f"Gemini Error: {e}")

    # 2. FALLBACK MELODY IF API FAILED
    if not melody_data:
        print("Using algorithmic melody.")
        melody_data = _generate_fallback_notes(scale_name, 50)


    # 3. RHYTHM ENFORCER (The Fix)
    # We ignore the AI's timing and impose our own "Game Pace"
    generated_track = []
    current_beat = 2.0  # Start with a small buffer
    note_counter = 0

    for note in melody_data:
        # Validate data
        if 'string' not in note or 'fret' not in note:
            continue
            
        spawn_time = int(current_beat * ticks_per_beat)
        
        generated_track.append({
            'string': note['string'],
            'fret': int(note['fret']),
            'note': 'X', 
            'spawn_time': spawn_time
        })

        # --- THE PACING LOGIC ---
        # 1. Standard Gap: Quarter Note (1 beat) or Half Note (2 beats)
        gap = random.choice([1.0, 1.0, 2.0]) 
        
        # 2. Phrase Logic: After 4 notes, force a longer rest (breathing room)
        note_counter += 1
        if note_counter >= 4:
            gap += 2.0  # Add 2 extra beats of rest
            note_counter = 0 # Reset phrase count
            
        current_beat += gap

        # Stop if we exceed duration
        if current_beat > (duration_seconds * (bpm / 60)):
            break

    print(f"Generated {len(generated_track)} notes with enforced rhythm.")
    return generated_track


def _generate_fallback_notes(scale_name, count):
    """Generates a list of valid notes without timing info."""
    STRING_OFFSETS = {"E": 4, "A": 9, "D": 14, "G": 19, "B": 23, "e": 28}
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    scale_notes = ['G', 'A', 'B', 'C', 'D', 'E', 'F#'] # Default G Major
    
    valid_positions = []
    for string_name, base_idx in STRING_OFFSETS.items():
        for fret in range(13):
            if NOTES[(base_idx + fret) % 12] in scale_notes:
                valid_positions.append({'string': string_name, 'fret': fret})
    
    return [random.choice(valid_positions) for _ in range(count)]