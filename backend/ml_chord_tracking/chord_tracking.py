## Main entry point

import time
import threading
import mediapipe as mp
import numpy as np
from .dataset import Dataset
from importlib.resources import files
from .parameters import CONFIDENCE_THRESHOLD, TOP_K_DISPLAY, SKELETON_COLOR
from .parameters import FONT, FONT_SCALE_TOP1, FONT_SCALE_OTHER, THICKNESS_TOP1, THICKNESS_OTHER
from .parameters import TEXT_X, TEXT_Y, TEXT_VERTICAL_SPACING, DEFAULT_INTERVAL, CHORDS
from .camera import run_camera_loop
from .hand_tracker import compute_features, FINGERS

# Whether or not to show any windows (cv2 windows or the Tk GUI)
SHOW_WINDOWS = True

# ================== MediaPipe setup ==================
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

latest_result = None

def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result


options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=str(files(__package__).joinpath("gesture_recognizer.task"))),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=result_callback,
)

# helper to expose latest_result to camera module
def get_latest_result():
    return latest_result

# ================== Dataset ==================
dataset = Dataset()

# Minimal headless GUI-like object for logging state when no GUI windows are shown
class HeadlessGUI:
    def __init__(self):
        self.tracking = False
        self.interval = DEFAULT_INTERVAL
        self.selected_chord = CHORDS[0]

# on_predictions will be called by camera module each frame with list[(label, conf)]
# (REPLACED) on_predictions now updates a global latest_preds so external importers can read the current prediction.
latest_preds = None  # stores the most recent list[(label, conf)]

def on_predictions(preds):
    global latest_preds
    latest_preds = preds
    if not preds:
        # print("Predictions: (none)")
        pass
    else:
        s = ", ".join(f"{label} - {conf*100:.0f}%" for label, conf in preds)
        # print(f"Predictions: {s}")

# New API: start/stop background processing and a simple getter for the top prediction.
_background_started = False
_stop_event = None
_camera_thread = None

def get_prediction():
    """
    Return the top predicted label string, or None if no prediction available.
    """
    global latest_preds
    if not latest_preds:
        return None
    try:
        top = latest_preds[0]
        return top[0] if top else None
    except Exception:
        return None

def _background_worker(show_windows):
    # create recognizer and run camera loop in this worker thread (recognizer lives in this scope)
    with GestureRecognizer.create_from_options(options) as recognizer:

        def submit_frame(rgb):
            # rgb is a numpy array in RGB order
            mp_image = mp.Image(mp.ImageFormat.SRGB, rgb)
            recognizer.recognize_async(mp_image, int(time.time() * 1000))

        if show_windows:
            # If caller asked for GUI, we still create a GestureGUI here,
            # but note that Tkinter usually needs to run on the main thread.
            # For background usage prefer show_windows=False.
            from gui import GestureGUI
            gui = GestureGUI(start_callback=None, stop_callback=None)
            gui.root.protocol("WM_DELETE_WINDOW", lambda: (_stop_event.set(), gui.root.destroy()))

            # run camera loop in another background thread so the worker can run gui.run()
            camera_thread = threading.Thread(
                target=run_camera_loop,
                kwargs=dict(
                    submit_frame=submit_frame,
                    get_latest_result=get_latest_result,
                    dataset=dataset,
                    gui=gui,
                    on_predictions=on_predictions,
                    show_windows=show_windows,
                    stop_event=_stop_event,
                ),
                daemon=True,
            )
            camera_thread.start()
            try:
                gui.run()
            finally:
                _stop_event.set()
                camera_thread.join(timeout=2)
        else:
            gui = HeadlessGUI()
            try:
                run_camera_loop(
                    submit_frame=submit_frame,
                    get_latest_result=get_latest_result,
                    dataset=dataset,
                    gui=gui,
                    on_predictions=on_predictions,
                    show_windows=show_windows,
                    stop_event=_stop_event,
                )
            except KeyboardInterrupt:
                pass

def start_in_background(show_windows=False):
    """
    Start the recognizer and camera loop in a background thread.
    By default runs headless (show_windows=False). Returns immediately.
    Call stop_background() to stop.
    """
    global _background_started, _stop_event, _camera_thread
    if _background_started:
        return
    _stop_event = threading.Event()
    _camera_thread = threading.Thread(target=_background_worker, args=(show_windows,), daemon=True)
    _camera_thread.start()
    _background_started = True

def stop_background(timeout=2.0):
    """
    Signal the background worker to stop and wait up to `timeout` seconds.
    """
    global _background_started, _stop_event, _camera_thread
    if not _background_started:
        return
    _stop_event.set()
    if _camera_thread is not None:
        _camera_thread.join(timeout=timeout)
    _background_started = False
    _camera_thread = None
    _stop_event = None

# ================== Main ==================
if __name__ == "__main__":
    # Provide a submit_frame function that creates mp.Image and calls recognizer
    with GestureRecognizer.create_from_options(options) as recognizer:

        def submit_frame(rgb):
            # rgb is a numpy array in RGB order
            mp_image = mp.Image(mp.ImageFormat.SRGB, rgb)
            recognizer.recognize_async(mp_image, int(time.time() * 1000))

        # choose GUI object (headless by default)
        if SHOW_WINDOWS:
            # Create the full GUI only when windows are enabled (keeps original behavior)
            from gui import GestureGUI
            gui = GestureGUI(start_callback=None, stop_callback=None)  # original callbacks not needed here

            # run the camera loop in a background thread so Tkinter mainloop can run in the main thread
            stop_event = threading.Event()
            # ensure closing the Tk window signals the camera thread to stop and then destroys the window
            gui.root.protocol("WM_DELETE_WINDOW", lambda: (stop_event.set(), gui.root.destroy()))

            camera_thread = threading.Thread(
                target=run_camera_loop,
                kwargs=dict(
                    submit_frame=submit_frame,
                    get_latest_result=get_latest_result,
                    dataset=dataset,
                    gui=gui,
                    on_predictions=on_predictions,
                    show_windows=SHOW_WINDOWS,
                    stop_event=stop_event,
                ),
                daemon=True,
            )
            camera_thread.start()

            try:
                # run the Tk event loop on the main thread (this will show the GUI)
                gui.run()
            finally:
                # ensure camera thread is instructed to stop and give it a moment to exit
                stop_event.set()
                camera_thread.join(timeout=2)
        else:
            gui = HeadlessGUI()

            # Run camera loop (this will capture frames, call submit_frame, compute features and predictions,
            # optionally show windows, and call on_predictions to allow main to print)
            try:
                run_camera_loop(submit_frame=submit_frame,
                                get_latest_result=get_latest_result,
                                dataset=dataset,
                                gui=gui,
                                on_predictions=on_predictions,
                                show_windows=SHOW_WINDOWS,
                                stop_event=None)
            except KeyboardInterrupt:
                pass
