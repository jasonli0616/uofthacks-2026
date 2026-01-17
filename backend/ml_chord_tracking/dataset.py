import os
from importlib.resources import files
import numpy as np
from .parameters import K, DIST_THRESHOLD

LOG_FILE = str(files(__package__).joinpath("dataset.txt"))

# Comment header explaining dataset format
COMMENT_HEADER = (
    "# label,"
    "index_bend,index_tip_dist,"
    "middle_bend,middle_tip_dist,"
    "ring_bend,ring_tip_dist,"
    "pinky_bend,pinky_tip_dist\n"
)

class Dataset:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self.X = []
        self.y = []
        self.load()

    def load(self):
        """Load dataset from file, ignoring comment lines."""
        if not os.path.exists(self.log_file):
            return

        with open(self.log_file, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue

                parts = line.strip().split(",")
                if len(parts) != 9:
                    continue

                label = parts[0]
                features = list(map(float, parts[1:]))
                self.X.append(features)
                self.y.append(label)

    def log(self, label, features):
        """
        Append a new sample.
        Writes the comment header only if the file does not exist yet.
        """
        file_exists = os.path.exists(self.log_file)

        with open(self.log_file, "a") as f:
            if not file_exists:
                f.write(COMMENT_HEADER)

            f.write(label + "," + ",".join(f"{v:.4f}" for v in features) + "\n")

        self.X.append(features)
        self.y.append(label)

    def predict(self, features):
        if len(self.X) < K:
            return ""

        X_np = np.array(self.X)
        dists = np.linalg.norm(X_np - features, axis=1)
        idx = np.argsort(dists)[:K]

        if dists[idx[0]] > DIST_THRESHOLD:
            return ""

        votes = {}
        for i in idx:
            votes[self.y[i]] = votes.get(self.y[i], 0) + 1

        return max(votes, key=votes.get)
