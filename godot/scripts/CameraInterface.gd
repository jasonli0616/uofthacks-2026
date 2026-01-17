# CameraInterface.gd
extends Node

signal chord_detected(chord_name: String)
signal finger_position_detected(string: String, fret: int)
signal note_played(note: String, string: String, fret: int)

# This will be replaced with actual computer vision integration
# For now, simulate input with keyboard

func _ready():
	# For testing purposes
	print("Camera interface ready. Awaiting chord detection...")

func simulate_chord_detection(chord_name: String):
	emit_signal("chord_detected", chord_name)

func simulate_finger_position(string: String, fret: int):
	emit_signal("finger_position_detected", string, fret)

func _process(delta):
	# When computer vision detects something
	if Input.is_action_just_pressed("test_chord"):  # For testing
		emit_signal("chord_detected", "C Major")
		emit_signal("note_played", "C", "E", 3)
