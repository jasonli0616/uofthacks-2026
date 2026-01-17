extends Node2D

@onready var player = $Player
@onready var note_detector = $NoteDetector
@onready var enemy_container = $EnemyContainer
@onready var test_controls = $TestControls

# Hardcoded enemy waves (chords)
var enemy_waves = [
	# Wave 1: C Major chord
	[
		{"string": "E", "note": "C", "fret": 0},
		{"string": "A", "note": "C", "fret": 3},
		{"string": "D", "note": "E", "fret": 2},
	],
	# Wave 2: G Major chord
	[
		{"string": "E", "note": "G", "fret": 3},
		{"string": "A", "note": "B", "fret": 2},
		{"string": "D", "note": "G", "fret": 0},
	],
	# Wave 3: A Minor chord
	[
		{"string": "E", "note": "A", "fret": 0},
		{"string": "A", "note": "A", "fret": 0},
		{"string": "D", "note": "E", "fret": 2},
	]
]

var current_wave = 0
var enemies_alive = 0

func _ready():
	print("Game started! Press keys 1-6 to play notes.")
	spawn_next_wave()

func spawn_next_wave():
	if current_wave >= enemy_waves.size():
		print("All waves complete!")
		return
	
	print("Spawning wave ", current_wave + 1)
	var wave_data = enemy_waves[current_wave]
	enemies_alive = wave_data.size()
	
	for enemy_data in wave_data:
		spawn_enemy(enemy_data)
	
	current_wave += 1

func spawn_enemy(enemy_data: Dictionary):
	var enemy_scene = preload("res://scenes/enemy.tscn")
	var enemy = enemy_scene.instantiate()
	enemy.position = Vector2(get_viewport_rect().size.x - 50, get_string_y(enemy_data.string))
	enemy.setup(enemy_data)
	enemy.add_to_group("enemies")
	
	# Connect enemy signals
	enemy.enemy_destroyed.connect(_on_enemy_destroyed)
	enemy.enemy_reached_player.connect(_on_enemy_reached_player)
	
	# Register with NoteDetector
	note_detector.register_enemy(enemy_data)
	
	enemy_container.add_child(enemy)

func get_string_y(string_name: String) -> float:
	var string_index = get_string_index(string_name)
	var viewport_size = get_viewport_rect().size
	return (string_index + 1) * viewport_size.y / 7

func get_string_index(string_name: String) -> int:
	match string_name.to_upper():
		"E": return 0
		"A": return 1
		"D": return 2
		"G": return 3
		"B": return 4
		"E2", "E_HIGH": return 5
		_: return 0

func _on_enemy_destroyed():
	enemies_alive -= 1
	print("Enemy destroyed! Remaining: ", enemies_alive)
	
	if enemies_alive <= 0:
		print("Wave cleared! Next wave in 2 seconds...")
		await get_tree().create_timer(2.0).timeout
		spawn_next_wave()

func _on_enemy_reached_player():
	player.take_damage(10)
