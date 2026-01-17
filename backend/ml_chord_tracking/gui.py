import tkinter as tk
from tkinter import ttk
from .parameters import DEFAULT_INTERVAL, CHORDS

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

        # Top static label (was dynamic before)
        ttk.Label(self.root, text="Select a label").pack(padx=10, pady=5)

        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=5)

        # Create a button for each chord
        for chord in CHORDS:
            btn = ttk.Button(button_frame, text=chord,
                             command=lambda c=chord: self.select_chord(c))
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Custom text input for label (new)
        self.custom_entry = ttk.Entry(self.root, width=30)
        self.custom_entry.pack(padx=10)
        # update display as user types
        self.custom_entry.bind("<KeyRelease>", self._on_custom_entry)

        # Interval input
        ttk.Label(self.root, text="Interval (s):").pack(padx=10, pady=5)
        self.interval_entry = ttk.Entry(self.root, width=10)
        self.interval_entry.insert(0, str(DEFAULT_INTERVAL))
        self.interval_entry.pack(padx=10)

        # Start/Stop toggle button (single button)
        self.toggle_btn = ttk.Button(self.root, text="Start Tracking", command=self._toggle)
        self.toggle_btn.pack(pady=5)

        # Status label (single status label used for updates)
        self.status = tk.StringVar(value=f"Selected chord: {self.selected_chord}")
        ttk.Label(self.root, textvariable=self.status).pack(pady=5)

        # Tracking state label
        self.tracking_var = tk.StringVar(value="Tracking: No")
        ttk.Label(self.root, textvariable=self.tracking_var).pack(pady=2)

    def select_chord(self, chord):
        """Set currently selected chord. Also clear custom input so buttons take effect."""
        self.selected_chord = chord
        # clear custom entry so the button choice is used
        try:
            self.custom_entry.delete(0, tk.END)
        except Exception:
            pass
        # update status only (top label is static now)
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
        """Call start_callback with the active label (custom text if present, else selected chord)."""
        label = self.get_active_label()
        if callable(self.start_callback):
            # pass the active label (string) to the callback
            self.start_callback(label)
        self.set_tracking(True)

    def _stop(self):
        """Call stop_callback (no args) and update tracking state."""
        if callable(self.stop_callback):
            self.stop_callback()
        self.set_tracking(False)

    # new toggle method to choose start or stop based on current state
    def _toggle(self):
        if self.tracking:
            self._stop()
        else:
            self._start()

    def _on_custom_entry(self, event=None):
        """Update status when user types in custom entry."""
        text = self.custom_entry.get().strip()
        if text:
            self.status.set(f"Custom label: {text}")
        else:
            # fall back to selected chord display
            self.status.set(f"Selected chord: {self.selected_chord}")

    def get_active_label(self) -> str:
        """Return the label that should be used: custom text if present, else selected chord."""
        text = self.custom_entry.get().strip()
        return text if text else self.selected_chord

    def run(self):
        self.root.mainloop()
    def run(self):
        self.root.mainloop()
