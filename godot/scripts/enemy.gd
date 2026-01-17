# Enemy.gd
extends Area2D

@onready var sprite = $Sprite2D
@onready var note_label = $NoteLabel
@onready var fret_label = $FretLabel

var speed = 100
var note_data = {}
var is_alive = true

func setup(data: Dictionary):
	note_data = data
	
	# Display note and fret information
	if note_label:
		note_label.text = data.note
	if fret_label:
		fret_label.text = str(data.fret)
	
	# Color code based on string
	var color = _get_string_color(data.string)
	sprite.modulate = color

func _process(delta):
	if is_alive:
		# Move towards player (left side)
		position.x -= speed * delta
		
		# Check if enemy reached player
		if position.x < 50:
			_reach_player()
			queue_free()

func _get_string_color(string_name: String) -> Color:
	match string_name.to_upper():
		"E": return Color(1, 0.2, 0.2)  # Red
		"A": return Color(1, 0.8, 0.2)  # Orange
		"D": return Color(0.2, 1, 0.2)  # Green
		"G": return Color(0.2, 0.6, 1)  # Blue
		"B": return Color(0.8, 0.2, 1)  # Purple
		"E2", "E_HIGH": return Color(1, 1, 0.2)  # Yellow
		_: return Color.WHITE

func _reach_player():
	# Signal to player that enemy reached them
	var player = get_tree().get_nodes_in_group("player")
	if player.size() > 0:
		player[0].take_damage(10)

func destroy():
	if is_alive:
		is_alive = false
		# Play destruction animation
		var tween = create_tween()
		tween.tween_property(sprite, "scale", Vector2(1.5, 1.5), 0.1)
		tween.tween_property(sprite, "scale", Vector2.ZERO, 0.2)
		tween.tween_callback(queue_free)
		
		# Signal successful attack
		var player = get_tree().get_nodes_in_group("player")
		if player.size() > 0:
			player[0].attack_successful()
