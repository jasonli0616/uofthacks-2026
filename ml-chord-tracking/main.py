import cv2
import time
import threading
from hand_tracker import compute_features, FINGERS
from dataset import Dataset
from gui import GestureGUI
import mediapipe as mp
import numpy as np
from parameters import CONFIDENCE_THRESHOLD, TOP_K_DISPLAY, SKELETON_COLOR
from parameters import FONT, FONT_SCALE_TOP1, FONT_SCALE_OTHER, THICKNESS_TOP1, THICKNESS_OTHER
from parameters import TEXT_X, TEXT_Y, TEXT_VERTICAL_SPACING, DEFAULT_INTERVAL, CHORDS

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
    base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=result_callback,
)

# ================== Dataset ==================
dataset = Dataset()

# ================== GUI Callbacks ==================
def start_tracking(gui: GestureGUI):
    gui.tracking = True
    try:
        gui.interval = float(gui.interval_entry.get())
    except:
        gui.interval = DEFAULT_INTERVAL
    gui.status.set(f"Tracking every {gui.interval:.2f}s")

def stop_tracking(gui: GestureGUI):
    gui.tracking = False
    gui.status.set("Stopped tracking")

# ================== Webcam thread ==================
def webcam_thread(gui: GestureGUI):
    global latest_result
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
    last_logged = 0

    with GestureRecognizer.create_from_options(options) as recognizer:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(mp.ImageFormat.SRGB, rgb)
            recognizer.recognize_async(mp_image, int(time.time() * 1000))

            current_features = None
            top_preds_unique = []

            if latest_result and latest_result.hand_landmarks:
                hand = latest_result.hand_landmarks[0]
                raw_pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
                current_features = compute_features(raw_pts)

                # Draw skeleton
                for finger in FINGERS.values():
                    mcp, pip, dip, tip = finger
                    for a, b in [(mcp, pip), (pip, dip), (dip, tip)]:
                        cv2.line(frame, raw_pts[a], raw_pts[b], SKELETON_COLOR, 2)
                    for i in finger:
                        cv2.circle(frame, raw_pts[i], 5, SKELETON_COLOR, -1)

                # Compute top-K predictions
                if len(dataset.X) >= TOP_K_DISPLAY:
                    X_np = np.array(dataset.X)
                    dists = np.linalg.norm(X_np - current_features, axis=1)
                    sorted_idx = np.argsort(dists)[:TOP_K_DISPLAY]

                    top_preds = []
                    for i in sorted_idx:
                        conf = max(0.0, 1.0 - dists[i] / 0.6)  # DIST_THRESHOLD hardcoded or import
                        if conf > CONFIDENCE_THRESHOLD:
                            top_preds.append((dataset.y[i], conf))

                    # Remove duplicates, keep first occurrence
                    seen = set()
                    for label, conf in top_preds:
                        if label not in seen:
                            top_preds_unique.append((label, conf))
                            seen.add(label)

                # Automatic logging
                current_time = time.time()
                if gui.tracking and current_features is not None:
                    if current_time - last_logged >= gui.interval:
                        label = gui.selected_chord  # use selected chord from buttons
                        if label:
                            dataset.log(label, current_features)
                            last_logged = current_time

            # Draw top predictions (small, black on white, vertical list)
            for rank, (label, conf) in enumerate(top_preds_unique[:TOP_K_DISPLAY]):
                text = f"{label} - {conf*100:.0f}%"
                y = TEXT_Y + rank * TEXT_VERTICAL_SPACING

                # White border
                cv2.putText(frame, text, (TEXT_X, y), FONT, FONT_SCALE_OTHER, (255, 255, 255),
                            THICKNESS_OTHER + 2, lineType=cv2.LINE_AA)
                # Black text
                cv2.putText(frame, text, (TEXT_X, y), FONT, FONT_SCALE_OTHER, (0, 0, 0),
                            THICKNESS_OTHER, lineType=cv2.LINE_AA)

            cv2.imshow("Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            if cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) < 1:
                break

    cap.release()
    cv2.destroyAllWindows()

# ================== Main ==================
if __name__ == "__main__":
    gui = GestureGUI(start_callback=start_tracking, stop_callback=stop_tracking)
    threading.Thread(target=webcam_thread, args=(gui,), daemon=True).start()
    gui.run()
