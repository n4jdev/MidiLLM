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

Use appropriate MIDI program numbers for instruments. Here's a comprehensive list:

0: Acoustic Grand Piano
1: Bright Acoustic Piano
2: Electric Grand Piano
3: Honky-tonk Piano
4: Electric Piano 1 (Rhodes)
5: Electric Piano 2 (Chorused)
6: Harpsichord
7: Clavinet
8: Celesta
9: Glockenspiel
10: Music Box
11: Vibraphone
12: Marimba
13: Xylophone
14: Tubular Bells
15: Dulcimer
16: Drawbar Organ
17: Percussive Organ
18: Rock Organ
19: Church Organ
20: Reed Organ
21: Accordion
22: Harmonica
23: Tango Accordion
24: Acoustic Guitar (nylon)
25: Acoustic Guitar (steel)
26: Electric Guitar (jazz)
27: Electric Guitar (clean)
28: Electric Guitar (muted)
29: Overdriven Guitar
30: Distortion Guitar
31: Guitar Harmonics
32: Acoustic Bass
33: Electric Bass (finger)
34: Electric Bass (pick)
35: Fretless Bass
36: Slap Bass 1
37: Slap Bass 2
38: Synth Bass 1
39: Synth Bass 2
40: Violin
41: Viola
42: Cello
43: Contrabass
44: Tremolo Strings
45: Pizzicato Strings
46: Orchestral Harp
47: Timpani
48: String Ensemble 1
49: String Ensemble 2
50: Synth Strings 1
51: Synth Strings 2
52: Choir Aahs
53: Voice Oohs
54: Synth Voice
55: Orchestra Hit
56: Trumpet
57: Trombone
58: Tuba
59: Muted Trumpet
60: French Horn
61: Brass Section
62: Synth Brass 1
63: Synth Brass 2
64: Soprano Sax
65: Alto Sax
66: Tenor Sax
67: Baritone Sax
68: Oboe
69: English Horn
70: Bassoon
71: Clarinet
72: Piccolo
73: Flute
74: Recorder
75: Pan Flute
76: Blown Bottle
77: Shakuhachi
78: Whistle
79: Ocarina
80: Lead 1 (square)
81: Lead 2 (sawtooth)
82: Lead 3 (calliope)
83: Lead 4 (chiff)
84: Lead 5 (charang)
85: Lead 6 (voice)
86: Lead 7 (fifths)
87: Lead 8 (bass + lead)
88: Pad 1 (new age)
89: Pad 2 (warm)
90: Pad 3 (polysynth)
91: Pad 4 (choir)
92: Pad 5 (bowed)
93: Pad 6 (metallic)
94: Pad 7 (halo)
95: Pad 8 (sweep)
96: FX 1 (rain)
97: FX 2 (soundtrack)
98: FX 3 (crystal)
99: FX 4 (atmosphere)
100: FX 5 (brightness)
101: FX 6 (goblins)
102: FX 7 (echoes)
103: FX 8 (sci-fi)
104: Sitar
105: Banjo
106: Shamisen
107: Koto
108: Kalimba
109: Bag pipe
110: Fiddle
111: Shanai
112: Tinkle Bell
113: Agogo
114: Steel Drums
115: Woodblock
116: Taiko Drum
117: Melodic Tom
118: Synth Drum
119: Reverse Cymbal
120: Guitar Fret Noise
121: Breath Noise
122: Seashore
123: Bird Tweet
124: Telephone Ring
125: Helicopter
126: Applause
127: Gunshot

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

Create a unique composition based on the user's input or request. Feel free to use any of the instruments listed above, and combine them creatively to match the user's requirements. Consider the genre, mood, and specific instrumentation requests when crafting your response.
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
