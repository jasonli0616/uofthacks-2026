extends Node2D

func _ready():
	draw_strings()

func draw_strings():
	var viewport_size = get_viewport_rect().size
	
	# String colors
	var colors = [
		Color(1, 0.2, 0.2),  # Red - E
		Color(1, 0.8, 0.2),  # Orange - A
		Color(0.2, 1, 0.2),  # Green - D
		Color(0.2, 0.6, 1),  # Blue - G
		Color(0.8, 0.2, 1),  # Purple - B
		Color(1, 1, 0.2),    # Yellow - e
	]
	
	# Create 6 horizontal lines (strings)
	for i in range(6):
		var line = Line2D.new()
		line.width = 3
		line.default_color = colors[i]
		
		var y_pos = (i + 1) * viewport_size.y / 7
		line.points = [
			Vector2(50, y_pos),
			Vector2(viewport_size.x - 50, y_pos)
		]
		
		add_child(line)
