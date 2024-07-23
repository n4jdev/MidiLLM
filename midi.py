import streamlit as st
import requests
import json
import time
import io
import pretty_midi
import numpy as np
import soundfile as sf

API_URL = "https://ffa.chat/api/chat/completions"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json",
    "authority": "ffa.chat",
    "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImVlN2JlMjg2LWQyNWEtNGI5Yy1hZTlhLTVjNTVjNzZiNTcwYSJ9.-vWeEQiW1m2E1K8SyDqgxeBfjomLuUfFX8Hz2bnJrq0",
    "origin": "https://ffa.chat",
    "referer": "https://ffa.chat/",
    "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

COOKIES = {
    "Hm_lvt_e1ab0b76810746f50a7929d521eee278": "1721296012",
    "Hm_lpvt_e1ab0b76810746f50a7929d521eee278": "1721296012",
    "HMACCOUNT": "A63480C9E06402CB",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImVlN2JlMjg2LWQyNWEtNGI5Yy1hZTlhLTVjNTVjNzZiNTcwYSJ9.-vWeEQiW1m2E1K8SyDqgxeBfjomLuUfFX8Hz2bnJrq0"
}

SYSTEM_PROMPT = """
You are MusicForge AI, a cutting-edge artificial intelligence specialized in creating sophisticated and nuanced musical compositions. Your goal is to generate innovative and precisely crafted musical pieces tailored to the user's requests.

Respond ONLY in the following JSON format:

{
    "composition_name": "String",
    "genre": "String",
    "tempo": Integer,
    "time_signature": "String",
    "key": "String",
    "instruments": [
        {
            "name": "String",
            "program": Integer,
            "notes": [
                {
                    "pitch": Integer,
                    "start_time": Float,
                    "duration": Float,
                    "velocity": Integer
                }
            ],
            "effects": ["String"]
        }
    ],
    "arrangement": "String",
    "mix_suggestions": "String",
    "creative_intentions": "String",
    "keywords": ["String"]
}

Notes:
- pitch: MIDI note number (0-127)
- start_time: Start time in seconds
- duration: Note duration in seconds
- velocity: MIDI velocity (0-127)
- program: MIDI program number (0-127) for instrument selection

Use appropriate MIDI program numbers for instruments. Some common ones:
0: Acoustic Grand Piano
24: Acoustic Guitar (nylon)
25: Acoustic Guitar (steel)
26: Electric Guitar (jazz)
27: Electric Guitar (clean)
33: Electric Bass (finger)
56: Trumpet
60: French Horn
73: Flute

Example Input: "Create a short, calm guitar beat"

Example Output:
{
    "composition_name": "Serene Strings",
    "genre": "Acoustic",
    "tempo": 70,
    "time_signature": "4/4",
    "key": "D Major",
    "instruments": [
        {
            "name": "Acoustic Guitar",
            "program": 25,
            "notes": [
                {"pitch": 62, "start_time": 0.0, "duration": 0.5, "velocity": 70},
                {"pitch": 59, "start_time": 0.5, "duration": 0.5, "velocity": 70},
                {"pitch": 57, "start_time": 1.0, "duration": 0.5, "velocity": 70},
                {"pitch": 55, "start_time": 1.5, "duration": 0.5, "velocity": 70},
                {"pitch": 62, "start_time": 2.0, "duration": 0.5, "velocity": 70},
                {"pitch": 59, "start_time": 2.5, "duration": 0.5, "velocity": 70},
                {"pitch": 57, "start_time": 3.0, "duration": 0.5, "velocity": 70},
                {"pitch": 55, "start_time": 3.5, "duration": 0.5, "velocity": 70}
            ],
            "effects": ["Light Reverb"]
        }
    ],
    "arrangement": "Simple 4-bar loop with arpeggiated chord progression",
    "mix_suggestions": "Add subtle room reverb to enhance the acoustic feel",
    "creative_intentions": "Create a peaceful and relaxing atmosphere with gentle guitar arpeggios",
    "keywords": ["calm", "acoustic", "guitar", "peaceful", "relaxing"]
}

Create a unique composition based on the user's input or request.
"""

@st.cache_data
def create_composition(user_input):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]
    
    data = {
        "model": "gemini-1.5-pro",
        "stream": False,
        "messages": messages,
        "chat_id": "d3ba18f6-4b98-4f9-a1ea-ac7258dd2b4d"
    }
    
    response = requests.post(API_URL, headers=HEADERS, cookies=COOKIES, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return json.loads(result['choices'][0]['message']['content'])
    else:
        return f"Error: {response.status_code} - {response.text}"

def create_midi(composition):
    midi = pretty_midi.PrettyMIDI()
    
    for instrument in composition['instruments']:
        midi_instrument = pretty_midi.Instrument(program=instrument['program'])
        
        for note in instrument['notes']:
            midi_note = pretty_midi.Note(
                velocity=note['velocity'],
                pitch=note['pitch'],
                start=note['start_time'],
                end=note['start_time'] + note['duration']
            )
            midi_instrument.notes.append(midi_note)
        
        midi.instruments.append(midi_instrument)
    
    return midi

def create_audio(midi):
    audio = midi.fluidsynth()
    return audio

def main():
    st.title("MusicForge AI - Music Composition Assistant")
    
    # Use session state to store the composition
    if 'composition' not in st.session_state:
        st.session_state.composition = None
    
    user_input = st.text_input("Enter your composition request:")
    
    if st.button("Generate Composition"):
        with st.spinner("Generating composition... Please wait."):
            start_time = time.time()
            st.session_state.composition = create_composition(user_input)
            end_time = time.time()
    
    # Display results if composition exists
    if st.session_state.composition:
        if isinstance(st.session_state.composition, str):  # Error occurred
            st.error(st.session_state.composition)
        else:
            st.success(f"Composition '{st.session_state.composition['composition_name']}' generated in {end_time - start_time:.2f} seconds.")
            
            st.subheader("Composition Details")
            st.json(st.session_state.composition)
            
            st.subheader("Generated Audio")
            midi = create_midi(st.session_state.composition)
            audio = create_audio(midi)
            
            # Convert audio to wav format
            buffer = io.BytesIO()
            sf.write(buffer, audio, 44100, format='wav')
            buffer.seek(0)
            
            st.audio(buffer, format="audio/wav")
            
            # Provide download buttons
            st.download_button(
                label="Download Audio (WAV)",
                data=buffer,
                file_name=f"{st.session_state.composition['composition_name']}.wav",
                mime="audio/wav"
            )
            
            midi_buffer = io.BytesIO()
            midi.write(midi_buffer)
            midi_buffer.seek(0)
            st.download_button(
                label="Download MIDI",
                data=midi_buffer,
                file_name=f"{st.session_state.composition['composition_name']}.mid",
                mime="audio/midi"
            )

if __name__ == "__main__":
    main()
