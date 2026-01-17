import aubio
import numpy as np
import sounddevice as sd
import math

# Audio settings
SAMPLE_RATE = 44100
BUFFER_SIZE = 2048
HOP_SIZE = 512

# Create aubio pitch detector
pitch_detector = aubio.pitch(
    method="yin",          # 'yin', 'yinfft', 'mcomb', 'fcomb', 'schmitt'
    buf_size=BUFFER_SIZE,
    hop_size=HOP_SIZE,
    samplerate=SAMPLE_RATE
)

pitch_detector.set_unit("Hz")
pitch_detector.set_tolerance(0.8)
pitch_detector.set_silence(-40)

def hz_to_note(freq):
    if freq <= 0:
        return "--"
    A4 = 440.0
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    n = round(12 * math.log2(freq / A4))
    note = notes[(n + 9) % 12]
    octave = 4 + (n + 9) // 12
    return f"{note}{octave}"

def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    # Convert input buffer to float32 numpy array
    samples = np.frombuffer(indata, dtype=np.float32)

    # Get pitch
    pitch = pitch_detector(samples)[0]
    confidence = pitch_detector.get_confidence()

    if pitch > 0 and confidence > 0.8:
        note = hz_to_note(pitch)
        print(f"{note:4}  {pitch:7.2f} Hz  conf={confidence:.2f}")

# Start audio stream
with sd.InputStream(
    channels=1,
    samplerate=SAMPLE_RATE,
    blocksize=HOP_SIZE,
    dtype='float32',
    callback=audio_callback
):
    print("Listening... Press Ctrl+C to stop")
    while True:
        sd.sleep(1000)
