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
pitch_detector.set_tolerance(0.5)
pitch_detector.set_silence(-40)

# New: store latest pitch/note and manage input stream
latest_pitch = None  # string note like "A4" or None
_stream = None

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
    global latest_pitch
    if status:
        # print(status) # Uncomment to debug buffer underflows/overflows
        pass

    # Convert input buffer to a 1-D float32 numpy array
    samples = indata[:, 0].astype(np.float32) if indata.ndim > 1 else indata.astype(np.float32)

    # Get pitch (aubio returns a buffer; take first element)
    pitch = float(pitch_detector(samples)[0])
    confidence = float(pitch_detector.get_confidence())

    if pitch > 0 and confidence > 0.8:
        note = hz_to_note(pitch)
        latest_pitch = note
    else:
        latest_pitch = None

def start_audio_stream():
    """
    Finds 'Aggregate Device', prints it, and starts the audio input stream.
    """
    global _stream
    if _stream is not None:
        return

    # --- DEVICE SELECTION LOGIC ---
    target_device_name = "Aggregate Device"
    selected_device_index = None
    selected_device_name = "Default"

    # List all devices and look for the target
    available_devices = sd.query_devices()
    
    for i, device in enumerate(available_devices):
        # We check if the name matches and if it actually has input channels
        if target_device_name in device['name'] and device['max_input_channels'] > 0:
            selected_device_index = i
            selected_device_name = device['name']
            break
    
    print(f"--------------------------------------------------")
    print(f"AUDIO INIT: Using Device: '{selected_device_name}'")
    print(f"AUDIO INIT: Device Index: {selected_device_index}")
    print(f"--------------------------------------------------")
    
    # ------------------------------

    try:
        _stream = sd.InputStream(
            device=selected_device_index, # Pass the specific device index here
            samplerate=SAMPLE_RATE,
            blocksize=HOP_SIZE,
            dtype='float32',
            channels=1,
            callback=audio_callback,
        )
        _stream.start()
    except Exception as e:
        print(f"ERROR: Could not open audio device '{selected_device_name}'.")
        print(f"Exception: {e}")

def stop_audio_stream():
    """
    Stop and close the audio input stream.
    """
    global _stream
    if _stream is None:
        return
    try:
        _stream.stop()
        _stream.close()
    finally:
        _stream = None

def get_pitch():
    """
    Return the most recent detected note string (e.g. 'A4') or None.
    """
    return latest_pitch