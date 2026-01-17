# Player.gd
extends Area2D

@onready var sprite = $Sprite2D
@onready var particles = $GPUParticles2D
@onready var animation_player = $AnimationPlayer

signal health_changed(new_health: int)
signal score_changed(new_score: int)
signal player_died()

var health = 100
var score = 0

func _ready():
	# Position player on the left side
	position = Vector2(100, get_viewport_rect().size.y / 2)
	particles.emitting = false

func take_damage(amount: int):
	health -= amount
	health = max(health, 0)
	emit_signal("health_changed", health)
	
	if health == 0:
		emit_signal("player_died")
	
	# Visual feedback
	sprite.modulate = Color.RED
	var tween = create_tween()
	tween.tween_property(sprite, "modulate", Color.WHITE, 0.3)
	
	if health <= 0:
		_game_over()

func attack_successful():
	score += 10
	_play_attack_animation()
	_emit_particles()

func _play_attack_animation():
	animation_player.play("attack")

func _emit_particles():
	particles.emitting = true
	await get_tree().create_timer(0.5).timeout
	particles.emitting = false

func _game_over():
	print("Game Over! Score: ", score)
	# Add game over logic here


func _on_note_detector_chord_played(chord_name: String) -> void:
	pass # Replace with function body.


func _on_note_detector_enemy_destroyed(enemy_data: Dictionary) -> void:
	pass # Replace with function body.


func _on_note_detector_note_played(note: String, fret: int, string: String) -> void:
	pass # Replace with function body.
