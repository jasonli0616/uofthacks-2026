import time

from .ml_chord_tracking import chord_tracking

def main(poll_interval=0.25):

    # Chord tracking
    chord_tracking.start_in_background(show_windows=True)

    try:
        while True:

            # Chord prediction
            chord_prediction = chord_tracking.get_prediction()
            if chord_prediction is not None:
                print(chord_prediction)


            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        chord_tracking.stop_background()

if __name__ == "__main__":
    main()