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

        # store callbacks
        self.start_callback = start_callback
        self.stop_callback = stop_callback

        # StringVar to show selected chord in the label
        self.chord_label_var = tk.StringVar(value=f"Select chord: {self.selected_chord}")

        # Chord selection label (now shows current chord)
        ttk.Label(self.root, textvariable=self.chord_label_var).pack(padx=10, pady=5)

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

        # Start/Stop toggle button (single button)
        self.toggle_btn = ttk.Button(self.root, text="Start Tracking", command=self._toggle)
        self.toggle_btn.pack(pady=5)

        # Status label
        self.status = tk.StringVar()
        ttk.Label(self.root, textvariable=self.status).pack(pady=5)

        # Tracking state label
        self.tracking_var = tk.StringVar(value="Tracking: No")
        ttk.Label(self.root, textvariable=self.tracking_var).pack(pady=2)

    def select_chord(self, chord):
        """Set currently selected chord"""
        self.selected_chord = chord
        # update chord label and status
        self.chord_label_var.set(f"Select chord: {chord}")
        self.status.set(f"Selected chord: {chord}")

    # new helper to set tracking state and update label
    def set_tracking(self, is_tracking: bool):
        self.tracking = is_tracking
        self.tracking_var.set(f"Tracking: {'Yes' if is_tracking else 'No'}")
        # update toggle button label to reflect new state
        if hasattr(self, "toggle_btn"):
            self.toggle_btn.config(text="Stop Tracking" if is_tracking else "Start Tracking")

    # wrappers around provided callbacks so UI reflects tracking state
    def _start(self):
        if callable(self.start_callback):
            self.start_callback(self)
        self.set_tracking(True)

    def _stop(self):
        if callable(self.stop_callback):
            self.stop_callback(self)
        self.set_tracking(False)

    # new toggle method to choose start or stop based on current state
    def _toggle(self):
        if self.tracking:
            self._stop()
        else:
            self._start()

    def run(self):
        self.root.mainloop()
