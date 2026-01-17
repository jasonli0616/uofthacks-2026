# Main.gd (updated)
extends Node2D

@onready var enemy_spawner = $EnemySpawner
@onready var strings_container = $GuitarStrings
@onready var player = $Player

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	enemy_spawner.enemies_received.connect(_on_enemies_received)
	_setup_guitar_strings()

func _setup_guitar_strings():
	# This will create 6 strings horizontally
	for i in range(6):
		var string_node = Node2D.new()
		string_node.name = "String_%d" % i
		strings_container.add_child(string_node)

func _on_enemies_received(enemies):
	print("Enemies received:", enemies)
	# Spawn enemies on their respective strings
	for enemy_data in enemies:
		_spawn_enemy_on_string(enemy_data)

func _spawn_enemy_on_string(enemy_data: Dictionary):
	# Extract string index from enemy data
	var string_index = _get_string_index(enemy_data.string)
	if string_index >= 0:
		var enemy_scene = preload("res://Scenes/Enemy.tscn")
		var enemy = enemy_scene.instantiate()
		enemy.setup(enemy_data)
		
		# Add to the appropriate string container
		var string_node = strings_container.get_node("String_%d" % string_index)
		string_node.add_child(enemy)

func _get_string_index(string_name: String) -> int:
	# Convert string names to indices (E=0, A=1, D=2, G=3, B=4, e=5)
	match string_name.to_upper():
		"E": return 0
		"A": return 1
		"D": return 2
		"G": return 3
		"B": return 4
		"E2": return 5
		"E_HIGH": return 5
		_: return -1

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_note_detector_note_played(note: String, fret: int, string: String) -> void:
	pass # Replace with function body.


func _on_note_detector_enemy_destroyed(enemy_data: Dictionary) -> void:
	pass # Replace with function body.


func _on_note_detector_chord_played(chord_name: String) -> void:
	pass # Replace with function body.
