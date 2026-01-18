"""
Top-level convenience API for easy imports from other projects.

Example:
  from backend import start_all, stop_all, get_chord, get_pitch
  start_all()            # starts chord tracking (headless) + audio
  chord = get_chord()    # returns predicted chord string or None
  pitch = get_pitch()    # returns predicted pitch string or None
  stop_all()             # stop services
"""

from .ml_chord_tracking import (
    start_chord as _start_chord,
    stop_chord as _stop_chord,
    get_chord as _get_chord,
    start_audio as _start_audio,
    stop_audio as _stop_audio,
    get_pitch as _get_pitch,
    start_all as _start_all,
    stop_all as _stop_all,
)

def start_chord(show_windows: bool = False):
    return _start_chord(show_windows=show_windows)

def stop_chord(timeout: float = 2.0):
    return _stop_chord(timeout=timeout)

def get_chord():
    return _get_chord()

def start_audio():
    try:
        return _start_audio()
    except Exception:
        pass

def stop_audio():
    try:
        return _stop_audio()
    except Exception:
        pass

def get_pitch():
    try:
        return _get_pitch()
    except Exception:
        return None

def start_all(show_windows: bool = False):
    return _start_all(show_windows=show_windows)

def stop_all(timeout: float = 2.0):
    return _stop_all(timeout=timeout)

__all__ = [
    "start_chord",
    "stop_chord",
    "get_chord",
    "start_audio",
    "stop_audio",
    "get_pitch",
    "start_all",
    "stop_all",
]