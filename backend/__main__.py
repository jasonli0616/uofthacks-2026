import time

from .ml_chord_tracking import chord_tracking
from .recognize_pitch import audio

def main(poll_interval=0.25):

    # Chord tracking
    chord_tracking.start_in_background(show_windows=False)

    # Start audio capture/processing
    audio.start_audio_stream()

    try:
        while True:

            # Chord prediction
            chord_prediction = chord_tracking.get_prediction()
            if chord_prediction is not None:
                print(chord_prediction)

            # Pitch prediction
            pitch_prediction = audio.get_pitch()  # returns note string or None
            if pitch_prediction is not None:
                print(pitch_prediction)


            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        chord_tracking.stop_background()
        audio.stop_audio_stream()

if __name__ == "__main__":
    main()