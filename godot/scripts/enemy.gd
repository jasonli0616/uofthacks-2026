extends Area2D

@onready var sprite = $Sprite2D
@onready var fret_label = $FretLabel

signal enemy_destroyed
signal enemy_reached_player

var speed = 150
var enemy_data = {}
var is_alive = true

func setup(data: Dictionary):
	enemy_data = data
	
	# Display fret
	fret_label.text = "Fret " + str(data.fret)
	
	# Color based on string
	var color = get_string_color(data.string)
	sprite.modulate = color

func _process(delta):
	if is_alive:
		# Move left toward player
		position.x -= speed * delta
		
		# Check if reached left side
		if position.x < 60:
			enemy_reached_player.emit()
			queue_free()

func get_string_color(string_name: String) -> Color:
	match string_name.to_upper():
		"E": return Color(1, 0.2, 0.2)  # Red
		"A": return Color(1, 0.8, 0.2)  # Orange
		"D": return Color(0.2, 1, 0.2)  # Green
		"G": return Color(0.2, 0.6, 1)  # Blue
		"B": return Color(0.8, 0.2, 1)  # Purple
		_: return Color(1, 1, 0.2)     # Yellow (for high E)

func destroy():
	if is_alive:
		is_alive = false
		enemy_destroyed.emit()
		
		# Destruction animation
		var tween = create_tween()
		tween.tween_property(sprite, "scale", Vector2(1.5, 1.5), 0.1)
		tween.tween_property(sprite, "scale", Vector2.ZERO, 0.2)
		tween.tween_callback(queue_free)
		
		print("Enemy destroyed: ", enemy_data)
