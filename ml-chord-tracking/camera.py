import time
import cv2
import numpy as np
from hand_tracker import compute_features, FINGERS
from parameters import CONFIDENCE_THRESHOLD, TOP_K_DISPLAY, SKELETON_COLOR
from parameters import FONT, FONT_SCALE_OTHER, THICKNESS_OTHER, TEXT_X, TEXT_Y, TEXT_VERTICAL_SPACING
from parameters import DIST_THRESHOLD

def run_camera_loop(submit_frame, get_latest_result, dataset, gui, on_predictions=None, show_windows=False, stop_event=None):
    """
    submit_frame(rgb): callable that accepts an RGB numpy array and sends it to MediaPipe.
    get_latest_result(): callable that returns the latest MediaPipe result (or None).
    dataset: Dataset instance used for logging / predictions.
    gui: object with attributes tracking (bool), interval (float), selected_chord (str).
    on_predictions: callable(list_of_(label,confidence)) invoked each frame.
    show_windows: whether to create cv2 windows / draw overlays.
    stop_event: optional threading.Event that, when set, will stop the camera loop.
    """
    cap = cv2.VideoCapture(0)
    if show_windows:
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)

    last_logged = 0

    try:
        # loop until capture closes or stop_event is set
        while cap.isOpened() and (stop_event is None or not stop_event.is_set()):
            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # send to mediapipe (main provides this)
            if callable(submit_frame):
                submit_frame(rgb)

            latest_result = None
            if callable(get_latest_result):
                latest_result = get_latest_result()

            current_features = None
            top_preds_unique = []

            if latest_result and getattr(latest_result, "hand_landmarks", None):
                hand = latest_result.hand_landmarks[0]
                raw_pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
                current_features = compute_features(raw_pts)

                # Draw skeleton (if windows enabled)
                for finger in FINGERS.values():
                    mcp, pip, dip, tip = finger
                    for a, b in [(mcp, pip), (pip, dip), (dip, tip)]:
                        if show_windows:
                            cv2.line(frame, raw_pts[a], raw_pts[b], SKELETON_COLOR, 2)
                    for i in finger:
                        if show_windows:
                            cv2.circle(frame, raw_pts[i], 5, SKELETON_COLOR, -1)

                # Compute top-K predictions
                if len(dataset.X) >= TOP_K_DISPLAY:
                    X_np = np.array(dataset.X)
                    dists = np.linalg.norm(X_np - current_features, axis=1)
                    sorted_idx = np.argsort(dists)[:TOP_K_DISPLAY]

                    top_preds = []
                    for i in sorted_idx:
                        conf = max(0.0, 1.0 - dists[i] / DIST_THRESHOLD)
                        if conf > CONFIDENCE_THRESHOLD:
                            top_preds.append((dataset.y[i], conf))

                    # Remove duplicates while preserving order
                    seen = set()
                    for label, conf in top_preds:
                        if label not in seen:
                            top_preds_unique.append((label, conf))
                            seen.add(label)

                # Automatic logging
                current_time = time.time()
                if getattr(gui, "tracking", False) and current_features is not None:
                    if current_time - last_logged >= getattr(gui, "interval", 0.2):
                        label = getattr(gui, "selected_chord", None)
                        if label:
                            dataset.log(label, current_features)
                            last_logged = current_time

            # Notify main about predictions (headless printing is done by main)
            if callable(on_predictions):
                on_predictions(top_preds_unique[:TOP_K_DISPLAY])

            # If windows are enabled, draw overlay text and show
            if show_windows:
                for rank, (label, conf) in enumerate(top_preds_unique[:TOP_K_DISPLAY]):
                    text = f"{label} - {conf*100:.0f}%"
                    y = TEXT_Y + rank * TEXT_VERTICAL_SPACING

                    # White border then black text for readability
                    cv2.putText(frame, text, (TEXT_X, y), FONT, FONT_SCALE_OTHER, (255, 255, 255),
                                THICKNESS_OTHER + 2, lineType=cv2.LINE_AA)
                    cv2.putText(frame, text, (TEXT_X, y), FONT, FONT_SCALE_OTHER, (0, 0, 0),
                                THICKNESS_OTHER, lineType=cv2.LINE_AA)

                cv2.imshow("Webcam", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                if cv2.getWindowProperty("Webcam", cv2.WND_PROP_VISIBLE) < 1:
                    break
                # allow an external stop request to break out promptly
                if stop_event is not None and stop_event.is_set():
                    break
            else:
                # small sleep to avoid very busy loop in headless mode
                time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        if show_windows:
            cv2.destroyAllWindows()
