import streamlit as st
import requests
import json
import time
import io
import pretty_midi
import numpy as np
import soundfile as sf
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

Examples:
Input 1:
"Create a jazzy piano piece with a mellow mood."

Output 1:
```json
{
    "composition_name": "Moonlit Melodies",
    "genre": "Jazz",
    "tempo": 92,
    "time_signature": "4/4",
    "key": "Eb Major",
    "duration": 180.5,
    "sections": [
        {
            "name": "Intro",
            "start_time": 0.0,
            "end_time": 16.0,
            "chord_progression": ["Ebmaj7", "Cm7", "Fm7", "Bb7"]
        },
        {
            "name": "Verse",
            "start_time": 16.0,
            "end_time": 80.0,
            "chord_progression": ["Ebmaj7", "Ab7", "Dm7b5", "G7", "Cm7", "Fm7", "Bb7", "Ebmaj7"]
        },
        {
            "name": "Bridge",
            "start_time": 80.0,
            "end_time": 112.0,
            "chord_progression": ["Abmaj7", "Bb7", "Gm7", "Cm7", "Fm7", "Bb7"]
        },
        {
            "name": "Outro",
            "start_time": 112.0,
            "end_time": 180.5,
            "chord_progression": ["Ebmaj7", "Cm7", "Fm7", "Bb7", "Ebmaj7"]
        }
    ],
    "instruments": [
        {
            "name": "Jazz Piano",
            "program": 0,
            "patterns": [
                {
                    "section": "Intro",
                    "notes": [
                        {
                            "pitch": 63,
                            "start_time": 0.0,
                            "duration": 0.5,
                            "velocity": 80
                        },
                        {
                            "pitch": 67,
                            "start_time": 0.5,
                            "duration": 0.5,
                            "velocity": 75
                        }
                    ]
                }
            ],
            "effects": {
                "reverb": 0.3,
                "chorus": 0.1,
                "delay": 0.0,
                "distortion": 0.0,
                "compressor": {
                    "threshold": -15.0,
                    "ratio": 2.5,
                    "attack": 0.005,
                    "release": 0.1
                }
            },
            "performance_style": "Smooth and flowing",
            "articulations": ["Legato", "Staccato"]
        }
    ],
    "arrangement": "Solo piano performance with dynamic variations",
    "mix_suggestions": {
        "eq": [{"instrument": "Jazz Piano", "frequency": 250, "gain": -2.0, "q": 0.7}],
        "compression": [{"instrument": "Jazz Piano", "threshold": -12.0, "ratio": 2.0}],
        "panning": [{"instrument": "Jazz Piano", "pan": 0.0}],
        "automation": [
            {
                "parameter": "Volume",
                "instrument": "Jazz Piano",
                "points": [{"time": 0.0, "value": 0.8}, {"time": 180.5, "value": 0.6}]
            }
        ]
    },
    "creative_intentions": "Create a relaxing and introspective jazz piano piece with subtle dynamic variations",
    "keywords": ["mellow", "introspective", "smooth", "relaxing"],
    "dynamics": [
        {
            "time": 0.0,
            "value": "mp"
        },
        {
            "time": 80.0,
            "value": "mf"
        },
        {
            "time": 112.0,
            "value": "p"
        }
    ],
    "modulations": [
        {
            "time": 80.0,
            "new_key": "Ab Major"
        },
        {
            "time": 112.0,
            "new_key": "Eb Major"
        }
    ],
    "tempo_changes": [
        {
            "time": 80.0,
            "new_tempo": 88
        },
        {
            "time": 112.0,
            "new_tempo": 84
        }
    ],
    "time_signature_changes": [],
    "arpeggiator": [],
    "sidechain": []
}
```

Input 2:
"Compose an energetic electronic dance track with a driving beat and synth leads."

Output 2:
```json
{
    "composition_name": "Neon Pulse",
    "genre": "Electronic Dance Music",
    "tempo": 128,
    "time_signature": "4/4",
    "key": "F Minor",
    "duration": 240.0,
    "sections": [
        {
            "name": "Intro",
            "start_time": 0.0,
            "end_time": 32.0,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Build-up",
            "start_time": 32.0,
            "end_time": 64.0,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Drop",
            "start_time": 64.0,
            "end_time": 128.0,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Breakdown",
            "start_time": 128.0,
            "end_time": 160.0,
            "chord_progression": ["Db", "Ab", "Bb", "Fm"]
        },
        {
            "name": "Drop 2",
            "start_time": 160.0,
            "end_time": 224.0,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        },
        {
            "name": "Outro",
            "start_time": 224.0,
            "end_time": 240.0,
            "chord_progression": ["Fm", "Ab", "Bb", "Db"]
        }
    ],
    "instruments": [
        {
            "name": "Kick",
            "program": 118,
            "patterns": [
                {
                    "section": "Drop",
                    "notes": [
                        {
                            "pitch": 36,
                            "start_time": 64.0,
                            "duration": 0.25,
                            "velocity": 120
                        },
                        {
                            "pitch": 36,
                            "start_time": 64.5,
                            "duration": 0.25,
                            "velocity": 120
                        }
                    ]
                }
            ],
            "effects": {
                "reverb": 0.1,
                "chorus": 0.0,
                "delay": 0.0,
                "distortion": 0.1,
                "compressor": {
                    "threshold": -6.0,
                    "ratio": 4.0,
                    "attack": 0.001,
                    "release": 0.05
                }
            },
            "performance_style": "Punchy and tight",
            "articulations": ["Short"]
        },
        {
            "name": "Synth Lead",
            "program": 81,
            "patterns": [
                {
                    "section": "Drop",
                    "notes": [
                        {
                            "pitch": 65,
                            "start_time": 64.0,
                            "duration": 0.25,
                            "velocity": 100
                        },
                        {
                            "pitch": 68,
                            "start_time": 64.25,
                            "duration": 0.25,
                            "velocity": 100
                        }
                    ]
                }
            ],
            "effects": {
                "reverb": 0.3,
                "chorus": 0.2,
                "delay": 0.2,
                "distortion": 0.2,
                "compressor": {
                    "threshold": -12.0,
                    "ratio": 2.5,
                    "attack": 0.005,
                    "release": 0.1
                }
            },
            "performance_style": "Aggressive and energetic",
            "articulations": ["Staccato", "Slide"]
        }
    ],
    "arrangement": "Typical EDM structure with build-ups and drops",
    "mix_suggestions": {
        "eq": [
            {"instrument": "Kick", "frequency": 60, "gain": 3.0, "q": 1.0},
            {"instrument": "Synth Lead", "frequency": 3000, "gain": 2.0, "q": 0.5}
        ],
        "compression": [
            {"instrument": "Kick", "threshold": -3.0, "ratio": 4.0},
            {"instrument": "Synth Lead", "threshold": -6.0, "ratio": 2.5}
        ],
        "panning": [
            {"instrument": "Kick", "pan": 0.0},
            {"instrument": "Synth Lead", "pan": 0.2}
        ],
        "automation": [
            {
                "parameter": "Cutoff",
                "instrument": "Synth Lead",
                "points": [{"time": 32.0, "value": 0.2}, {"time": 64.0, "value": 1.0}]
            }
        ]
    },
    "creative_intentions": "Create an energetic and euphoric EDM track with a powerful drop and infectious synth melodies",
    "keywords": ["energetic", "driving", "euphoric", "pulsating"],
    "dynamics": [
        {
            "time": 0.0,
            "value": "mf"
        },
        {
            "time": 64.0,
            "value": "ff"
        },
        {
            "time": 128.0,
            "value": "mp"
        },
        {
            "time": 160.0,
            "value": "ff"
        }
    ],
    "modulations": [],
    "tempo_changes": [],
    "time_signature_changes": [],
    "arpeggiator": [
        {
            "instrument": "Synth Lead",
            "pattern": "Up",
            "rate": "1/16",
            "octave_range": 2
        }
    ],
    "sidechain": [
        {
            "source_instrument": "Kick",
            "target_instrument": "Synth Lead",
            "amount": 0.7
        }
    ]
}

Create a unique composition based on the user's input or request. Consider the genre, mood, and specific instrumentation requests when crafting your response. Ensure that the composition is between 30-300 seconds long.""" # System prompt removed as requested

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
    tempo_changes = composition.get('tempo_changes', [])
    if tempo_changes:
        tempo_change_times = [change['time'] for change in tempo_changes]
        tempo_change_tempos = [change['new_tempo'] for change in tempo_changes]
        
        # Ensure the first tempo change is at the beginning
        if tempo_change_times[0] > 0:
            tempo_change_times.insert(0, 0)
            tempo_change_tempos.insert(0, composition['tempo'])
        
        midi.tempo_changes = [
            pretty_midi.TempoChange(tempo=tempo, time=time)
            for tempo, time in zip(tempo_change_tempos, tempo_change_times)
        ]
    
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

def create_audio(midi, sample_rate=44100, max_duration=300):
    try:
        if not any(instrument.notes for instrument in midi.instruments):
            return np.zeros(int(sample_rate))  # Return 1 second of silence

        end_time = min(max(max(note.end for note in instrument.notes) for instrument in midi.instruments), max_duration)
        audio = np.zeros(int(end_time * sample_rate))
        
        for instrument in midi.instruments:
            for note in instrument.notes:
                t = np.linspace(0, note.end - note.start, int((note.end - note.start) * sample_rate), False)
                freq = pretty_midi.note_number_to_hz(note.pitch)
                note_audio = (note.velocity / 127.0) * np.sin(2 * np.pi * freq * t)
                
                start_sample = int(note.start * sample_rate)
                end_sample = start_sample + len(note_audio)
                
                if end_sample > len(audio):
                    end_sample = len(audio)
                    note_audio = note_audio[:end_sample - start_sample]
                
                audio[start_sample:end_sample] += note_audio
        
        # Normalize audio
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        
        if np.isnan(audio).any() or np.isinf(audio).any():
            print("Warning: NaN or Inf values detected in audio")
            audio = np.nan_to_num(audio)  # Replace NaN and Inf with valid values
        
        return audio
    except Exception as e:
        print(f"Error in create_audio: {str(e)}")
        return np.zeros(int(sample_rate))  # Return 1 second of silence

def plot_piano_roll(midi, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    for instrument in midi.instruments:
        for note in instrument.notes:
            ax.bar(note.start, note.pitch, width=note.end - note.start, 
                   alpha=0.7, align='edge', 
                   color=plt.cm.Set3(instrument.program / 128.0))
    
    ax.set_ylim(0, 127)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('MIDI Note Number')
    ax.set_title('Piano Roll Visualization')
    
    return ax

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
            plot_piano_roll(midi, ax=ax)
            st.pyplot(fig)

if __name__ == "__main__":
    main()
