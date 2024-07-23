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

Create a unique composition based on the user's input or request. Consider the genre, mood, and specific instrumentation requests when crafting your response. Ensure that the composition is between 30-300 seconds long.
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

def create_audio(midi, sample_rate=44100):
    # Find the end time of the last note
    end_time = max(max(note.end for note in instrument.notes) for instrument in midi.instruments)
    
    # Create a sine wave representation of the MIDI
    audio = np.zeros(int(end_time * sample_rate))
    
    for instrument in midi.instruments:
        for note in instrument.notes:
            t = np.linspace(0, note.end - note.start, int((note.end - note.start) * sample_rate), False)
            freq = pretty_midi.note_number_to_hz(note.pitch)
            note_audio = (note.velocity / 127.0) * np.sin(2 * np.pi * freq * t)
            
            start_sample = int(note.start * sample_rate)
            end_sample = start_sample + len(note_audio)
            audio[start_sample:end_sample] += note_audio
    
    # Normalize audio
    audio = audio / np.max(np.abs(audio))
    return audio

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
