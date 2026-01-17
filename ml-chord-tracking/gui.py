import tkinter as tk
from tkinter import ttk
from parameters import DEFAULT_INTERVAL, CHORDS

class GestureGUI:
    def __init__(self, start_callback, stop_callback):
        self.tracking = False
        self.interval = DEFAULT_INTERVAL
        self.selected_chord = CHORDS[0]  # default

        self.root = tk.Tk()
        self.root.title("Gesture Logger")

        # Chord selection label
        ttk.Label(self.root, text="Select chord:").pack(padx=10, pady=5)

        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5)

        # Create a button for each chord
        for chord in CHORDS:
            btn = ttk.Button(button_frame, text=chord,
                             command=lambda c=chord: self.select_chord(c))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Interval input
        ttk.Label(self.root, text="Interval (s):").pack(padx=10, pady=5)
        self.interval_entry = ttk.Entry(self.root, width=10)
        self.interval_entry.insert(0, str(DEFAULT_INTERVAL))
        self.interval_entry.pack(padx=10)

        # Start / Stop buttons
        ttk.Button(self.root, text="Start Tracking", command=lambda: start_callback(self)).pack(pady=5)
        ttk.Button(self.root, text="Stop Tracking", command=lambda: stop_callback(self)).pack(pady=5)

        # Status label
        self.status = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status).pack(pady=5)

    def select_chord(self, chord):
        """Set currently selected chord"""
        self.selected_chord = chord
        self.status.set(f"Selected chord: {chord}")

    def run(self):
        self.root.mainloop()
