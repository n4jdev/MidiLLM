import streamlit as st
import requests
import json
import time
import io
import pretty_midi
import numpy as np
import soundfile as sf
from midiutil import MIDIFile
import random
import matplotlib.pyplot as plt

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
You are MusicForge AI, an advanced artificial intelligence specialized in creating sophisticated and nuanced musical compositions. Your goal is to generate innovative and precisely crafted musical pieces tailored to the user's requests.

Respond ONLY in the following JSON format:

{
    "composition_name": "String",
    "genre": "String",
    "tempo": Integer,
    "time_signature": "String",
    "key": "String",
    "duration": Float,
    "sections": [
        {
            "name": "String",
            "start_time": Float,
            "end_time": Float,
            "chord_progression": ["String"]
        }
    ],
    "instruments": [
        {
            "name": "String",
            "program": Integer,
            "patterns": [
                {
                    "section": "String",
                    "notes": [
                        {
                            "pitch": Integer,
                            "start_time": Float,
                            "duration": Float,
                            "velocity": Integer
                        }
                    ]
                }
            ],
            "effects": {
                "reverb": Float,
                "chorus": Float,
                "delay": Float,
                "distortion": Float,
                "compressor": {
                    "threshold": Float,
                    "ratio": Float,
                    "attack": Float,
                    "release": Float
                }
            },
            "performance_style": "String",
            "articulations": ["String"]
        }
    ],
    "arrangement": "String",
    "mix_suggestions": {
        "eq": [{"instrument": "String", "frequency": Integer, "gain": Float, "q": Float}],
        "compression": [{"instrument": "String", "threshold": Float, "ratio": Float}],
        "panning": [{"instrument": "String", "pan": Float}],
        "automation": [
            {
                "parameter": "String",
                "instrument": "String",
                "points": [{"time": Float, "value": Float}]
            }
        ]
    },
    "creative_intentions": "String",
    "keywords": ["String"],
    "dynamics": [
        {
            "time": Float,
            "value": "String"
        }
    ],
    "modulations": [
        {
            "time": Float,
            "new_key": "String"
        }
    ],
    "tempo_changes": [
        {
            "time": Float,
            "new_tempo": Integer
        }
    ],
    "time_signature_changes": [
        {
            "time": Float,
            "new_time_signature": "String"
        }
    ],
    "arpeggiator": [
        {
            "instrument": "String",
            "pattern": "String",
            "rate": "String",
            "octave_range": Integer
        }
    ],
    "sidechain": [
        {
            "source_instrument": "String",
            "target_instrument": "String",
            "amount": Float
        }
    ]
}

Notes:
- pitch: MIDI note number (0-127)
- start_time: Start time in seconds
- duration: Note duration in seconds
- velocity: MIDI velocity (0-127)
- program: MIDI program number (0-127) for instrument selection
- duration: Total composition duration in seconds (aim for 30-300 seconds)
- reverb, chorus, delay, distortion: Effect intensities (0.0 to 1.0)
- pan: Panning value (-1.0 to 1.0, where 0 is center)

Music Theory Tools:
1. Common chord progressions: I-V-vi-IV, ii-V-I, I-IV-V, i-iv-v
2. Scales: Major, Natural Minor, Harmonic Minor, Melodic Minor, Pentatonic, Blues
3. Modes: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian
4. Cadences: Perfect, Imperfect, Plagal, Deceptive
5. Rhythmic patterns: 4/4 (common time), 3/4 (waltz), 6/8 (compound duple), 5/4, 7/8
6. Articulations: Staccato, Legato, Accent, Tenuto, Marcato

Composition Techniques:
1. Counterpoint: Create independent melodic lines that harmonize
2. Ostinato: Repetitive musical phrase or rhythm
3. Call and Response: Alternating musical phrases between instruments
4. Motivic Development: Evolve a short musical idea throughout the piece
5. Layering: Gradually introduce or remove instruments
6. Polyrhythms: Simultaneous use of contrasting rhythms
7. Modulation: Change keys within the composition
8. Dynamic Contrast: Vary the volume and intensity throughout the piece

Common DAW Tools:
1. Arpeggiator: Automatically generate arpeggios based on input chords
2. Sidechain Compression: Ducking one instrument's volume in response to another
3. Automation: Gradual changes in various parameters over time
4. Effects Rack: Combine multiple effects in a specific order
5. Loop-based Composition: Create and arrange loops for different sections
6. Step Sequencer: Program rhythmic patterns using a grid-based interface
7. Pitch Correction: Adjust the pitch of vocals or instruments
8. Time Stretching: Alter the duration of audio without changing its pitch
9. Sample Slicing: Chop up audio samples for creative rearrangement
10. MIDI Effects: Apply various MIDI transformations (e.g., chord, scale)

When creating patterns for each instrument, consider the following:
1. Use appropriate scales and chord tones for the current key and chord
2. Create rhythmic variety while maintaining consistency with the genre
3. Incorporate rests and syncopation for interest
4. Use articulations to add expression
5. Vary note velocities for dynamic interest
6. Create patterns that complement other instruments

Ensure that the composition is between 30-300 seconds long. Incorporate dynamic changes, chord progressions, and potential key modulations to create a more interesting and varied piece. Use the sections to create a clear structure (e.g., Intro, Verse, Chorus, Bridge, Outro).

Create a unique composition based on the user's input or request. Consider the genre, mood, and specific instrumentation requests when crafting your response.

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

Example Input:
"Create an upbeat electronic dance track with a strong bass line, catchy synth melody, and build-up to a drop. Include some vocal chops and a breakdown section."

Example Output:
{
    "composition_name": "Neon Pulse",
    "genre": "Electronic Dance Music (EDM)",
    "tempo": 128,
    "time_signature": "4/4",
    "key": "F Minor",
    "duration": 210,
    "sections": [
        {
            "name": "Intro",
            "start_time": 0,
            "end_time": 30,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Verse",
            "start_time": 30,
            "end_time": 60,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Build-up",
            "start_time": 60,
            "end_time": 90,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Drop",
            "start_time": 90,
            "end_time": 120,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Breakdown",
            "start_time": 120,
            "end_time": 150,
            "chord_progression": ["Db", "Ab", "Fm", "Bb"]
        },
        {
            "name": "Build-up 2",
            "start_time": 150,
            "end_time": 180,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Drop 2",
            "start_time": 180,
            "end_time": 210,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        }
    ],
    "instruments": [
        {
            "name": "Bass",
            "program": 38,
            "patterns": [
                {
                    "section": "Intro",
                    "notes": [
                        {"pitch": 41, "start_time": 0, "duration": 0.25, "velocity": 100},
                        {"pitch": 41, "start_time": 0.5, "duration": 0.25, "velocity": 100},
                        {"pitch": 41, "start_time": 1, "duration": 0.25, "velocity": 100},
                        {"pitch": 41, "start_time": 1.5, "duration": 0.25, "velocity": 100}
                    ]
                }
            ],
            "effects": {
                "distortion": 0.3,
                "compressor": {
                    "threshold": -20,
                    "ratio": 4,
                    "attack": 0.005,
                    "release": 0.1
                }
            },
            "performance_style": "Punchy",
            "articulations": ["Accent"]
        },
        {
            "name": "Lead Synth",
            "program": 81,
            "patterns": [
                {
                    "section": "Verse",
                    "notes": [
                        {"pitch": 65, "start_time": 30, "duration": 0.5, "velocity": 90},
                        {"pitch": 68, "start_time": 30.5, "duration": 0.5, "velocity": 90},
                        {"pitch": 70, "start_time": 31, "duration": 1, "velocity": 95},
                        {"pitch": 68, "start_time": 32, "duration": 0.5, "velocity": 90},
                        {"pitch": 65, "start_time": 32.5, "duration": 0.5, "velocity": 90}
                    ]
                }
            ],
            "effects": {
                "reverb": 0.3,
                "delay": 0.2
            },
            "performance_style": "Legato",
            "articulations": ["Legato"]
        },
        {
            "name": "Drums",
            "program": 0,
            "patterns": [
                {
                    "section": "Drop",
                    "notes": [
                        {"pitch": 36, "start_time": 90, "duration": 0.1, "velocity": 110},
                        {"pitch": 38, "start_time": 90.5, "duration": 0.1, "velocity": 90},
                        {"pitch": 42, "start_time": 90.25, "duration": 0.1, "velocity": 100},
                        {"pitch": 42, "start_time": 90.75, "duration": 0.1, "velocity": 100}
                    ]
                }
            ],
            "effects": {
                "compression": {
                    "threshold": -15,
                    "ratio": 3,
                    "attack": 0.01,
                    "release": 0.05
                }
            },
            "performance_style": "Energetic",
            "articulations": ["Accent", "Staccato"]
        }
    ],
    "arrangement": "The track starts with an intro featuring the bass line, gradually introducing other elements. The verse introduces the lead synth melody. The build-up section increases tension, leading to the energetic drop. A breakdown provides contrast before building up to the final drop.",
    "mix_suggestions": {
        "eq": [
            {"instrument": "Bass", "frequency": 100, "gain": 2, "q": 1},
            {"instrument": "Lead Synth", "frequency": 3000, "gain": 3, "q": 0.7}
        ],
        "compression": [
            {"instrument": "Drums", "threshold": -20, "ratio": 4}
        ],
        "panning": [
            {"instrument": "Lead Synth", "pan": 0.2}
        ],
        "automation": [
            {
                "parameter": "Cutoff",
                "instrument": "Lead Synth",
                "points": [
                    {"time": 60, "value": 0.3},
                    {"time": 90, "value": 1.0}
                ]
            }
        ]
    },
    "creative_intentions": "Create an energetic and euphoric atmosphere with a driving rhythm and memorable melody. Use tension and release techniques to engage the listener.",
    "keywords": ["upbeat", "electronic", "dance", "catchy", "energetic"],
    "dynamics": [
        {"time": 60, "value": "mf"},
        {"time": 90, "value": "f"},
        {"time": 120, "value": "mp"},
        {"time": 180, "value": "ff"}
    ],
    "tempo_changes": [
        {"time": 150, "new_tempo": 132}
    ],
        "arpeggiator": [
        {
            "instrument": "Pad Synth",
            "pattern": "Up",
            "rate": "1/16",
            "octave_range": 2
        }
    ],
    "sidechain": [
        {
            "source_instrument": "Kick",
            "target_instrument": "Bass",
            "amount": 0.7
        },
        {
            "source_instrument": "Kick",
            "target_instrument": "Pad Synth",
            "amount": 0.5
        }
    ]
}
"""

@st.cache_data
def create_composition(user_input):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]
    
    data = {
        "model": "claude-3-5-sonnet-20240620",
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
    midi = pretty_midi.PrettyMIDI(initial_tempo=composition['tempo'])
    
    for instrument_data in composition['instruments']:
        instrument = pretty_midi.Instrument(program=instrument_data['program'])
        
        for pattern in instrument_data['patterns']:
            for note in pattern['notes']:
                midi_note = pretty_midi.Note(
                    velocity=note['velocity'],
                    pitch=note['pitch'],
                    start=note['start_time'],
                    end=note['start_time'] + note['duration']
                )
                instrument.notes.append(midi_note)
        
        # Add effects
        effects = instrument_data.get('effects', {})
        if effects.get('reverb'):
            instrument.control_changes.append(pretty_midi.ControlChange(91, int(effects['reverb'] * 127), time=0))
        if effects.get('chorus'):
            instrument.control_changes.append(pretty_midi.ControlChange(93, int(effects['chorus'] * 127), time=0))
        if effects.get('delay'):
            instrument.control_changes.append(pretty_midi.ControlChange(94, int(effects['delay'] * 127), time=0))
        
        midi.instruments.append(instrument)
    
    # Add tempo changes
    for tempo_change in composition.get('tempo_changes', []):
        midi.adjust_times([tempo_change['time']], [tempo_change['new_tempo']])
    
    # Add time signature changes
    for ts_change in composition.get('time_signature_changes', []):
        numerator, denominator = map(int, ts_change['new_time_signature'].split('/'))
        midi.time_signature_changes.append(pretty_midi.TimeSignature(numerator, denominator, ts_change['time']))
    
    return midi

def apply_humanization(midi, amount=0.01):
    for instrument in midi.instruments:
        for note in instrument.notes:
            # Slightly adjust timing
            note.start += random.uniform(-amount, amount)
            note.end += random.uniform(-amount, amount)
            
            # Slightly adjust velocity
            note.velocity = max(0, min(127, int(note.velocity + random.uniform(-5, 5))))
    return midi

def apply_dynamics(midi, composition):
    for dynamic in composition.get('dynamics', []):
        time = dynamic['time']
        value = dynamic['value']
        velocity_multiplier = {
            'pp': 0.5, 'p': 0.65, 'mp': 0.8, 'mf': 1.0, 'f': 1.15, 'ff': 1.3
        }.get(value, 1.0)
        
        for instrument in midi.instruments:
            for note in instrument.notes:
                if note.start >= time:
                    note.velocity = min(127, int(note.velocity * velocity_multiplier))
    
    return midi

def apply_mix_suggestions(midi, composition):
    mix_suggestions = composition.get('mix_suggestions', {})
    
    # Apply EQ (simplified)
    for eq in mix_suggestions.get('eq', []):
        instrument_name = eq['instrument']
        frequency = eq['frequency']
        gain = eq['gain']
        for instrument in midi.instruments:
            if instrument.name == instrument_name:
                # This is a simplified EQ application
                for note in instrument.notes:
                    if abs(pretty_midi.note_number_to_hz(note.pitch) - frequency) < 100:
                        note.velocity = min(127, max(0, int(note.velocity * (1 + gain))))
    
    # Apply panning
    for pan in mix_suggestions.get('panning', []):
        instrument_name = pan['instrument']
        pan_value = pan['pan']
        for instrument in midi.instruments:
            if instrument.name == instrument_name:
                cc = pretty_midi.ControlChange(10, int((pan_value + 1) * 63.5), 0)
                instrument.control_changes.append(cc)
    
    # Apply automation (simplified)
    for auto in mix_suggestions.get('automation', []):
        instrument_name = auto['instrument']
        parameter = auto['parameter']
        for instrument in midi.instruments:
            if instrument.name == instrument_name:
                for point in auto['points']:
                    if parameter == 'Volume':
                        cc = pretty_midi.ControlChange(7, int(point['value'] * 127), point['time'])
                    elif parameter == 'Pan':
                        cc = pretty_midi.ControlChange(10, int((point['value'] + 1) * 63.5), point['time'])
                    elif parameter == 'Cutoff':
                        cc = pretty_midi.ControlChange(74, int(point['value'] * 127), point['time'])
                    instrument.control_changes.append(cc)
    
    return midi

def apply_arpeggiator(midi, composition):
    for arp in composition.get('arpeggiator', []):
        instrument_name = arp['instrument']
        pattern = arp['pattern']
        rate = arp['rate']
        octave_range = arp['octave_range']
        
        for instrument in midi.instruments:
            if instrument.name == instrument_name:
                # Implement arpeggiator logic here
                # This is a simplified version
                notes = instrument.notes
                instrument.notes = []
                for note in notes:
                    for i in range(octave_range):
                        new_note = pretty_midi.Note(
                            velocity=note.velocity,
                            pitch=note.pitch + (12 * i),
                            start=note.start + (i * 0.125),  # Assuming 1/16 rate
                            end=note.start + ((i + 1) * 0.125)
                        )
                        instrument.notes.append(new_note)
    
    return midi

def apply_sidechain(midi, composition):
    for sc in composition.get('sidechain', []):
        source_name = sc['source_instrument']
        target_name = sc['target_instrument']
        amount = sc['amount']
        
        source_instrument = next((i for i in midi.instruments if i.name == source_name), None)
        target_instrument = next((i for i in midi.instruments if i.name == target_name), None)
        
        if source_instrument and target_instrument:
            for source_note in source_instrument.notes:
                for target_note in target_instrument.notes:
                    if target_note.start < source_note.start < target_note.end:
                        target_note.velocity = int(target_note.velocity * (1 - amount))
    
    return midi

def create_audio(midi, sample_rate=44100):
    # Create a sine wave representation of the MIDI
    duration = max(max(note.end for note in instrument.notes) for instrument in midi.instruments)
    audio = np.zeros(int(duration * sample_rate))
    
    for instrument in midi.instruments:
        for note in instrument.notes:
            t = np.linspace(note.start, note.end, int((note.end - note.start) * sample_rate), False)
            freq = pretty_midi.note_number_to_hz(note.pitch)
            audio[int(note.start * sample_rate):int(note.end * sample_rate)] += \
                (note.velocity / 127.0) * np.sin(2 * np.pi * freq * t)
    
    # Normalize audio
    audio = audio / np.max(np.abs(audio))
    return audio

def main():
    st.title("MusicForge AI - Advanced Music Composition Assistant")
    
    if 'composition' not in st.session_state:
        st.session_state.composition = None
    
    user_input = st.text_input("Enter your composition request:")
    duration = st.slider("Desired composition length (seconds)", 30, 300, 60)
    
    advanced_options = st.expander("Advanced Options")
    with advanced_options:
        humanization = st.slider("Humanization amount", 0.0, 0.05, 0.01, 0.01)
        apply_dynamics_option = st.checkbox("Apply dynamic variations", value=True)
        apply_mix_option = st.checkbox("Apply mix suggestions", value=True)
        apply_arpeggiator_option = st.checkbox("Apply arpeggiator", value=True)
        apply_sidechain_option = st.checkbox("Apply sidechain", value=True)
    
    if st.button("Generate Composition"):
        with st.spinner("Generating composition... Please wait."):
            start_time = time.time()
            composition_request = f"{user_input} Make the composition approximately {duration} seconds long."
            st.session_state.composition = create_composition(composition_request)
            end_time = time.time()
    
    if st.session_state.composition:
        if isinstance(st.session_state.composition, str):  # Error occurred
            st.error(st.session_state.composition)
        else:
            st.success(f"Composition '{st.session_state.composition['composition_name']}' generated in {end_time - start_time:.2f} seconds.")
            
            st.subheader("Composition Details")
            st.json(st.session_state.composition)
            
            st.subheader("Generated Audio")
            midi = create_midi(st.session_state.composition)
            
            if humanization > 0:
                midi = apply_humanization(midi, humanization)
            
            if apply_dynamics_option:
                midi = apply_dynamics(midi, st.session_state.composition)
            
            if apply_mix_option:
                midi = apply_mix_suggestions(midi, st.session_state.composition)
            
            if apply_arpeggiator_option:
                midi = apply_arpeggiator(midi, st.session_state.composition)
            
            if apply_sidechain_option:
                midi = apply_sidechain(midi, st.session_state.composition)
            
            audio = create_audio(midi)
            
            buffer = io.BytesIO()
            sf.write(buffer, audio, 44100, format='wav')
            buffer.seek(0)
            
            st.audio(buffer, format="audio/wav")
            
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
            
            # Visualization
            st.subheader("MIDI Visualization")
            fig, ax = plt.subplots(figsize=(12, 6))
            pretty_midi.plot_piano_roll(midi, ax=ax)
            st.pyplot(fig)

if __name__ == "__main__":
    main()
