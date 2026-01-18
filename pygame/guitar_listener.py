import pyaudio
import numpy as np
import aubio
import threading
import time
import math

# --- CONFIGURATION ---
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024  
HOP_SIZE = 512      
CONFIDENCE_THRESH = 0.8  

# Notes for mapping MIDI numbers
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Global State
_stream = None
_pa = None
_running = False
_current_pitch = None
_pitch_lock = threading.Lock()

def start_audio_stream():
    global _pa, _stream, _running
    if _running: return

    _running = True
    _pa = pyaudio.PyAudio()
    
    try:
        _stream = _pa.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=HOP_SIZE
        )
        threading.Thread(target=_listen_loop, daemon=True).start()
        print("🎸 Audio Stream Started (Polling Mode)")
    except Exception as e:
        print(f"Failed to start audio: {e}")
        _running = False

def stop_audio_stream():
    global _pa, _stream, _running
    _running = False
    if _stream:
        try:
            _stream.stop_stream()
            _stream.close()
        except: pass
    if _pa:
        _pa.terminate()

def get_pitch():
    """Returns the currently detected note (e.g. 'A2') or None."""
    with _pitch_lock:
        # We return the latest pitch. 
        # Optional: You can set _current_pitch to None here if you only want to read it once.
        return _current_pitch

def _listen_loop():
    global _current_pitch
    
    # Initialize Aubio
    pitch_detector = aubio.pitch("default", BUFFER_SIZE, HOP_SIZE, SAMPLE_RATE)
    pitch_detector.set_unit("Hz")
    pitch_detector.set_tolerance(0.8)

    while _running:
        try:
            data = _stream.read(HOP_SIZE, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.float32)

            pitch = pitch_detector(samples)[0]
            confidence = pitch_detector.get_confidence()

            detected_note = None

            # Filter noise
            if confidence >= CONFIDENCE_THRESH and pitch > 60:
                detected_note = _freq_to_note(pitch)

            # Update global state safely
            with _pitch_lock:
                _current_pitch = detected_note
                
        except Exception as e:
            print(f"Audio Loop Error: {e}")
            time.sleep(0.1)

def _freq_to_note(freq):
    if freq == 0: return None
    try:
        # Calculate MIDI number
        midi_number = 69 + 12 * math.log2(freq / 440.0)
        rounded_midi = int(round(midi_number))
        
        # Determine Note Name and Octave
        note_name = NOTE_NAMES[rounded_midi % 12]
        octave = int(rounded_midi / 12) - 1
        
        return f"{note_name}{octave}"
    except:
        return None