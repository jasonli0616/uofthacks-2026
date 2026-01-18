import asyncio

import json
import os
from google import genai
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# Guided output generation schema
class Enemy(BaseModel):
    string: str = Field(description="Which of 6 standard guitar string the enemy is associated with")
    note: str = Field(description="The musical note the enemy represents")
    fret: int = Field(description="The fret number the enemy is associated with on the specified string")

# Array format for multiple enemies
class Enemies(BaseModel):
    enemies: List[Enemy] = Field(description="List of enemy types")

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# Send the request to the Gemini API to generate enemies
def generate_enemies(key, num_enemies):
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



