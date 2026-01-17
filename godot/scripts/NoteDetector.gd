# NoteDetector.gd
extends Node

signal note_played(note: String, fret: int, string: String)
signal chord_played(chord_name: String)
signal enemy_destroyed(enemy_data: Dictionary)

var current_enemies = []

func register_enemy(enemy_data: Dictionary):
	current_enemies.append(enemy_data)
	
func enemy_hit_success(enemy_data: Dictionary):
	# Emit signal when enemy is destroyed
	emit_signal("enemy_destroyed", enemy_data)

func check_played_note(played_note: String, played_fret: int, played_string: String):
	# Find matching enemy
	for enemy_data in current_enemies:
		if (enemy_data.note == played_note and 
			enemy_data.fret == played_fret and 
			enemy_data.string.to_upper() == played_string.to_upper()):
			
			# Found a match!
			emit_signal("note_played", played_note, played_fret, played_string)
			
			# Remove from list
			current_enemies.erase(enemy_data)
			
			# Find and destroy the enemy node
			_destroy_matching_enemy(enemy_data)
			return true
	
	return false

func _destroy_matching_enemy(enemy_data: Dictionary):
	# Find enemy node with matching data
	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		if enemy.note_data == enemy_data:
			enemy.destroy()
			break


func _on_camera_interface_chord_detected(chord_name: String) -> void:
	pass # Replace with function body.


func _on_camera_interface_finger_position_detected(string: String, fret: int) -> void:
	pass # Replace with function body.


func _on_camera_interface_note_played(note: String, string: String, fret: int) -> void:
	pass # Replace with function body.
