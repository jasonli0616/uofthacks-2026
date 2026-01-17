extends Node

signal enemies_received(enemies)

var socket = WebSocketPeer.new()
var request_sent = false # Flag to ensure we only send once

func _ready():
	print("Attempting to connect...")
	var err = socket.connect_to_url("ws://127.0.0.1:6677")
	if err != OK:
		print("Error connecting to server.")
		set_process(false)

func _process(_delta):
	# CRITICAL: You must poll every frame to keep the connection alive
	socket.poll()
	
	var state = socket.get_ready_state()
	
	if state == WebSocketPeer.STATE_OPEN:
		
		# 1. If connected and we haven't sent yet, SEND NOW
		if not request_sent:
			_send_request()
			request_sent = true
			
		# 2. Check for incoming messages (The Response)
		while socket.get_available_packet_count() > 0:
			var message = socket.get_packet().get_string_from_utf8()
			print("SUCCESS! Received from Python: ")
			print(message)
			
			var parsed = JSON.parse_string(message)
			if parsed == null:
				print("ERROR: Failed to parse JSON")
				continue

			if not parsed.has("enemies"):
				print("ERROR: JSON has no 'enemies' field")
				continue
			
			emit_signal("enemies_received", parsed["enemies"])
			
			# Optional: Disconnect after we get our answer
			socket.close()
			print("Test complete. Disconnecting.")

	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed. Code: %d, Reason: %s" % [code, reason])
		set_process(false) # Stop processing

func _send_request():
	print("Connection established. Sending JSON request...")
	var payload = {
		"key": "G Major",
		"num_enemies": 4
	}
	# Convert dictionary to JSON string
	socket.send_text(JSON.stringify(payload))
	
