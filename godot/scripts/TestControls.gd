# TestInputHandler.gd
extends Node
class_name CameraInterface

@export var camera_interface: CameraInterface

func _input(event):
	# Simulate playing individual notes
	if event.is_action_pressed("test_note_1"):
		camera_interface.simulate_finger_position("E", 3)
		camera_interface.emit_signal("note_played", "G", "E", 3)
	
	if event.is_action_pressed("test_note_2"):
		camera_interface.simulate_finger_position("A", 2)
		camera_interface.emit_signal("note_played", "B", "A", 2)
	
	# Simulate chords
	if event.is_action_pressed("test_chord_c"):
		camera_interface.simulate_chord_detection("C Major")
	
	if event.is_action_pressed("test_chord_g"):
		camera_interface.simulate_chord_detection("G Major")
