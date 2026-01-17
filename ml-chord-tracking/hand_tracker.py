import math
import numpy as np

FINGERS = {
    "Index":  [5, 6, 7, 8],
    "Middle": [9, 10, 11, 12],
    "Ring":   [13, 14, 15, 16],
    "Pinky":  [17, 18, 19, 20],
}

def angle(a, b, c):
    """
    Angle at point b between points a-b-c
    Handles zero-length vectors and floating point errors.
    """
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    mag = np.linalg.norm(ba) * np.linalg.norm(bc)
    if mag < 1e-6:
        return 0.0
    cos_angle = np.dot(ba, bc) / mag
    cos_angle = min(1.0, max(-1.0, cos_angle))
    return math.degrees(math.acos(cos_angle))

def normalize_hand(pts):
    wrist = np.array(pts[0])
    middle_mcp = np.array(pts[9])

    centered = [np.array(p) - wrist for p in pts]

    direction = middle_mcp - wrist
    theta = -math.atan2(direction[0], direction[1])
    R = np.array([[math.cos(theta), -math.sin(theta)],
                  [math.sin(theta), math.cos(theta)]])

    rotated = [R @ p for p in centered]

    palm_size = np.linalg.norm(rotated[9])
    if palm_size == 0:
        palm_size = 1.0

    normalized = [p / palm_size for p in rotated]
    return normalized

def compute_features(pts):
    normalized = normalize_hand(pts)
    features = []
    for idx in FINGERS.values():
        mcp, pip, dip, tip = idx
        ang = angle(normalized[mcp], normalized[pip], normalized[dip])
        tip_dist = np.linalg.norm(normalized[tip])
        features.extend([ang / 180.0, tip_dist])
    return features
