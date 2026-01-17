import cv2

# Threshold for showing predictions (0.0 - 1.0)
CONFIDENCE_THRESHOLD = 0.5

# Number of top predictions to display
TOP_K_DISPLAY = 3

# kNN parameters
K = 3
DIST_THRESHOLD = 0.6

# Automatic logging interval (seconds)
DEFAULT_INTERVAL = 0.2

# Skeleton drawing color (BGR)
SKELETON_COLOR = (64, 224, 208)  # soft teal

# Font parameters for overlay text
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_TOP1 = 0.7
FONT_SCALE_OTHER = 0.7
THICKNESS_TOP1 = 2
THICKNESS_OTHER = 2

# Overlay text position
TEXT_X = 10
TEXT_Y = 30
TEXT_VERTICAL_SPACING = 25


CHORDS = ["A", "B", "C", "D", "E", "F", "G"]
