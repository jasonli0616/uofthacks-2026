import os
import numpy as np
from parameters import K, DIST_THRESHOLD

LOG_FILE = "dataset.txt"

class Dataset:
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self.X = []
        self.y = []
        self.load()

    def load(self):
        if not os.path.exists(self.log_file):
            return
        with open(self.log_file, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 9:
                    continue
                label = parts[0]
                features = list(map(float, parts[1:]))
                self.X.append(features)
                self.y.append(label)

    def log(self, label, features):
        with open(self.log_file, "a") as f:
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
