import asyncio
import pyaudio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # Load environment variables from a .env file if present

# Longer buffer reduces chance of audio drop, but also delays audio and user commands.
BUFFER_SECONDS = 1
CHUNK = 4200
FORMAT = pyaudio.paInt16
CHANNELS = 2
MODEL = 'models/lyria-realtime-exp'
OUTPUT_RATE = 48000

api_key = os.environ.get("GOOGLE_API_KEY")

if api_key is None:
    # Only ask for input if running directly, otherwise this might block your game
    print("Please enter your API key")
    api_key = input("API Key: ").strip()

client = genai.Client(
    api_key=api_key,
    http_options={'api_version': 'v1alpha',}, # v1alpha since Lyria RealTime is only experimental
)

# CHANGED: Renamed from main() to match your import and added arguments
async def start_music_session(instrument="Electric Guitar", genre="Rock", mood="Energetic", bpm=120):
    p = pyaudio.PyAudio()
    config = types.LiveMusicGenerationConfig()
    async with client.aio.live.music.connect(model=MODEL) as session:
        async def receive():
            chunks_count = 0
            output_stream = p.open(
                format=FORMAT, channels=CHANNELS, rate=OUTPUT_RATE, output=True, frames_per_buffer=CHUNK)
            async for message in session.receive():
                chunks_count += 1
                if chunks_count == 1:
                    # Introduce a delay before starting playback to have a buffer for network jitter.
                    await asyncio.sleep(BUFFER_SECONDS)
                
                if message.server_content:
                    audio_data = message.server_content.audio_chunks[0].data
                    output_stream.write(audio_data)
                elif message.filtered_prompt:
                    print("Prompt was filtered out: ", message.filtered_prompt)
                else:
                    # Occasional empty messages are normal
                    pass
                await asyncio.sleep(10**-12)

        async def send():
            await asyncio.sleep(5) # Allow initial prompt to play a bit

            # NOTE: usage of input() here might conflict if your game takes over the console.
            # But we leave it for now so you can still control it if you run from a terminal.
            while True:
                print("Set new prompt ((bpm=<number|'AUTO'>, scale=<enum|'AUTO'>, top_k=<number|'AUTO'>, 'play', 'pause', 'prompt1:w1,prompt2:w2,...', or single text prompt)")
                
                # We use asyncio.to_thread to prevent input() from blocking the audio loop
                prompt_str = await asyncio.to_thread(input, " > ")

                if not prompt_str: 
                    continue

                if prompt_str.lower() == 'q':
                    print("Sending STOP command.")
                    await session.stop()
                    return False

                if prompt_str.lower() == 'play':
                    print("Sending PLAY command.")
                    await session.play()
                    continue

                if prompt_str.lower() == 'pause':
                    print("Sending PAUSE command.")
                    await session.pause()
                    continue

                if prompt_str.startswith('bpm='):
                  if prompt_str.strip().endswith('AUTO'):
                    del config.bpm
                    print(f"Setting BPM to AUTO, which requires resetting context.")
                  else:
                    bpm_value = int(prompt_str.removeprefix('bpm='))
                    print(f"Setting BPM to {bpm_value}, which requires resetting context.")
                    config.bpm=bpm_value
                  await session.set_music_generation_config(config=config)
                  await session.reset_context()
                  continue

                if prompt_str.startswith('scale='):
                  if prompt_str.strip().endswith('AUTO'):
                    del config.scale
                    print(f"Setting Scale to AUTO, which requires resetting context.")
                  else:
                    found_scale_enum_member = None
                    for scale_member in types.Scale: 
                        if scale_member.name.lower() == prompt_str.lower():
                            found_scale_enum_member = scale_member
                            break
                    if found_scale_enum_member:
                        print(f"Setting scale to {found_scale_enum_member.name}, which requires resetting context.")
                        config.scale = found_scale_enum_member
                    else:
                        print("Error: Matching enum not found.")
                  await session.set_music_generation_config(config=config)
                  await session.reset_context()
                  continue

                if prompt_str.startswith('top_k='):
                    top_k_value = int(prompt_str.removeprefix('top_k='))
                    print(f"Setting TopK to {top_k_value}.")
                    config.top_k = top_k_value
                    await session.set_music_generation_config(config=config)
                    await session.reset_context()
                    continue

                if ":" in prompt_str:
                    parsed_prompts = []
                    segments = prompt_str.split(',')
                    malformed_segment_exists = False 

                    for segment_str_raw in segments:
                        segment_str = segment_str_raw.strip()
                        if not segment_str: 
                            continue

                        parts = segment_str.split(':', 1)

                        if len(parts) == 2:
                            text_p = parts[0].strip()
                            weight_s = parts[1].strip()

                            if not text_p: 
                                print(f"Error: Empty prompt text in segment '{segment_str_raw}'. Skipping.")
                                malformed_segment_exists = True
                                continue 
                            try:
                                weight_f = float(weight_s) 
                                parsed_prompts.append(types.WeightedPrompt(text=text_p, weight=weight_f))
                            except ValueError:
                                print(f"Error: Invalid weight in segment '{segment_str_raw}'. Skipping.")
                                malformed_segment_exists = True
                                continue 
                        else:
                            print(f"Error: Segment '{segment_str_raw}' not in 'text:weight' format. Skipping.")
                            malformed_segment_exists = True
                            continue 

                    if parsed_prompts: 
                        prompt_repr = [f"'{p.text}':{p.weight}" for p in parsed_prompts]
                        if malformed_segment_exists:
                            print(f"Partially sending valid prompts: {', '.join(prompt_repr)}")
                        else:
                            print(f"Sending multiple weighted prompts: {', '.join(prompt_repr)}")
                        await session.set_weighted_prompts(prompts=parsed_prompts)
                    else: 
                        print("Error: No valid 'text:weight' segments found.")
                    continue

                print(f"Sending single text prompt: \"{prompt_str}\"")
                await session.set_weighted_prompts(
                    prompts=[types.WeightedPrompt(text=prompt_str, weight=1.0)]
                )

        
        # CHANGED: Use the arguments passed into the function instead of hardcoded strings
        print(f"Initializing Lyria with: {instrument}, {genre}, {mood} @ {bpm} BPM")
        await session.set_weighted_prompts(
            prompts=[types.WeightedPrompt(text=instrument, weight=0.5),
                     types.WeightedPrompt(text=genre, weight=0.8),
                     types.WeightedPrompt(text=mood, weight=0.5)]
        )

        # CHANGED: Use the bpm argument
        config.bpm = int(bpm)
        config.scale = types.Scale.G_MAJOR_E_MINOR 
        await session.set_music_generation_config(config=config)

        await session.play()

        send_task = asyncio.create_task(send())
        receive_task = asyncio.create_task(receive())

        # Don't quit the loop until tasks are done
        await asyncio.gather(send_task, receive_task)

    # Clean up PyAudio
    p.terminate()

# CHANGED: This protects the code from running when imported!
if __name__ == "__main__":
    asyncio.run(start_music_session())