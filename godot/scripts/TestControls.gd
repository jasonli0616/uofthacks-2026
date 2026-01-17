extends Node

@onready var note_detector = $"../NoteDetector"

func _input(event):
	# Press keys 1-6 to play strings
	if event is InputEventKey and event.pressed:
		var string_played = ""
		
		match event.keycode:
			KEY_1:
				string_played = "E"
			KEY_2:
				string_played = "A"
			KEY_3:
				string_played = "D"
			KEY_4:
				string_played = "G"
			KEY_5:
				string_played = "B"
			KEY_6:
				string_played = "e"
			_:
				return  # Ignore other keys
		
		print("Playing string: ", string_played)
		note_detector.check_played_note(string_played)
