import time
import socket
import json

from .ml_chord_tracking import chord_tracking
from .recognize_pitch import audio

def main(poll_interval=0.25):

    # Chord tracking
    chord_tracking.start_in_background(show_windows=False)

    # Start audio capture/processing
    audio.start_audio_stream()

    # create UDP socket (send-only)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_target = ("127.0.0.1", 6678)

    try:
        while True:

            # Chord prediction
            chord_prediction = chord_tracking.get_prediction()
            # print(chord_prediction)

            # Pitch prediction
            pitch_prediction = audio.get_pitch()  # returns note string or None
            # print(pitch_prediction)

            # Send through UDP sockets
            payload = json.dumps({
                "chord": chord_prediction,
                "pitch": pitch_prediction
            })
            try:
                sock.sendto(payload.encode("utf-8"), udp_target)
            except Exception:
                # keep loop running even if send fails
                pass

            time.sleep(poll_interval)
    except KeyboardInterrupt:
        pass
    finally:
        chord_tracking.stop_background()
        audio.stop_audio_stream()
        try:
            sock.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
