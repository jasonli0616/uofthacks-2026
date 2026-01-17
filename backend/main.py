import time

# start/stop and getter for live predictions
from .ml_chord_tracking.chord_tracking import start_in_background, get_prediction, stop_background

def main(poll_interval=0.25):
    # start headless background processing
    start_in_background(show_windows=False)

    try:
        while True:
            pred = get_prediction()  # returns top label string or None
            print(pred)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        stop_background()

if __name__ == "__main__":
    main()
