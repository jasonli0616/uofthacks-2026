extends Area2D

@onready var sprite = $Sprite2D

var health = 100
var score = 0

func _ready():
	# Position player on the left side
	position = Vector2(50, get_viewport_rect().size.y / 2)

func take_damage(amount: int):
	health -= amount
	health = max(health, 0)
	print("Player health: ", health)
	
	# Visual feedback
	sprite.modulate = Color.RED
	var tween = create_tween()
	tween.tween_property(sprite, "modulate", Color.WHITE, 0.3)
	
	if health <= 0:
		game_over()

func add_score(points: int):
	score += points
	print("Score: ", score)

func game_over():
	print("GAME OVER! Final score: ", score)
	get_tree().reload_current_scene()
