extends Node

signal correct_note_played
signal incorrect_note_played

var current_enemies = []  # Store enemy data

func register_enemy(enemy_data: Dictionary):
	current_enemies.append(enemy_data)
	print("Registered enemy: ", enemy_data)

func check_played_note(played_string: String):
	print("Checking note on string: ", played_string)
	
	# Find if any enemy is on this string
	var string_enemies = []
	for enemy in current_enemies:
		if enemy.string.to_upper() == played_string.to_upper():
			string_enemies.append(enemy)
	
	if string_enemies.size() > 0:
		# Found enemy on this string - destroy the first one
		var enemy_to_destroy = string_enemies[0]
		current_enemies.erase(enemy_to_destroy)
		destroy_enemy_node(enemy_to_destroy)
		correct_note_played.emit()
		return true
	else:
		# No enemy on this string
		incorrect_note_played.emit()
		print("Miss! No enemy on string ", played_string)
		return false

func destroy_enemy_node(enemy_data: Dictionary):
	# Find the enemy node in the scene and destroy it
	var enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in enemies:
		if enemy.enemy_data == enemy_data:
			enemy.destroy()
			break
