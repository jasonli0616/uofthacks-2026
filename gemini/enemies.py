import asyncio
import websockets
import json
import os
from google import genai
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# --- 1. Define Models ---
class Enemy(BaseModel):
    string: str = Field(description="Which of 6 standard guitar string the enemy is associated with")
    note: str = Field(description="The musical note the enemy represents")
    fret: int = Field(description="The fret number the enemy is associated with on the specified string")

class Enemies(BaseModel):
    enemies: List[Enemy] = Field(description="List of enemy types")

# --- 2. Setup Configuration ---
load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

# Initialize the client (Synchronous client)
client = genai.Client(api_key=api_key)

# --- 3. Helper function to run blocking GenAI calls ---
def generate_enemies_sync(key, num_enemies):
    """
    This function runs the blocking API call. 
    We will offload this to a separate thread so the async loop doesn't freeze.
    """
    prompt = (
        f"Give me {num_enemies} enemies for a guitar learning game for a song in the key of {key}. "
        f"For each enemy, provide the string (E, A, D, G, B, e), note (e.g., A, A#, B, etc.), "
        f"and fret number (0-12) it is associated with. Respond in JSON format."
    )
    
    response = client.models.generate_content(
        model="gemini-2.0-flash", # Updated to a current model ID, adjust if needed
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Enemies.model_json_schema(),
        }
    )
    return response.text

# --- 4. Async Websocket Handler ---
async def handler(websocket):
    print(f"Client connected: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            print(f"Received raw message: {message}")
            
            # Parse JSON from Godot
            try:
                data = json.loads(message)
                key = data.get("key", "C")
                num_enemies = data.get("num_enemies", 5)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
                continue

            print(f"Processing: key={key}, num_enemies={num_enemies}")

            # Run the blocking GenAI call in a separate thread
            # This is CRITICAL for async servers; otherwise, the server hangs 
            # for everyone while waiting for Google.
            loop = asyncio.get_running_loop()
            response_text = await loop.run_in_executor(
                None, 
                generate_enemies_sync, 
                key, 
                num_enemies
            )
            
            # Send result back to Godot
            print("Sending response...")
            await websocket.send(response_text)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

# --- 5. Main Entry Point ---
async def main():
    # Start the websocket server on localhost:6677
    async with websockets.serve(handler, "localhost", 6677):
        print("Async WebSocket Server listening on ws://localhost:6677")
        # Keep the server running indefinitely
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopping...")