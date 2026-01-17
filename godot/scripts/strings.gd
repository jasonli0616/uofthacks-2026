# GuitarStrings.gd
extends Node2D

var string_colors = [
	Color(1, 0.2, 0.2, 0.7),  # Low E - Red
	Color(1, 0.8, 0.2, 0.7),  # A - Orange
	Color(0.2, 1, 0.2, 0.7),  # D - Green
	Color(0.2, 0.6, 1, 0.7),  # G - Blue
	Color(0.8, 0.2, 1, 0.7),  # B - Purple
	Color(1, 1, 0.2, 0.7)     # High E - Yellow
]

func _ready():
	# Create visual representation of strings
	for i in range(6):
		_create_string_visual(i)

func _create_string_visual(string_index: int):
	var line = Line2D.new()
	line.width = 2
	line.default_color = string_colors[string_index]
	
	# Calculate positions
	var viewport_size = get_viewport_rect().size
	var y_pos = (string_index + 1) * viewport_size.y / 7
	
	line.points = [
		Vector2(50, y_pos),
		Vector2(viewport_size.x - 50, y_pos)
	]
	
	add_child(line)
