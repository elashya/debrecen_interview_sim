# utils.py
import streamlit as st
from openai import OpenAI
import tempfile
import os
import numpy as np
import soundfile as sf
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# ✅ OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# === GPT QUESTION HANDLER ===
def ask_gpt_question(history, topic):
    messages = [
        {"role": "system", "content": f"""You are conducting a University of Debrecen entrance interview.
Ask ONE question at a time in a calm, formal tone.
Current topic: {topic}.
Keep it clear and spoken-friendly. The student answers by voice. Total ~8 questions: 2 personal, 3 biology, 3 chemistry.
Avoid repeating previous questions."""}
    ]

    for qa in history:
        messages.append({"role": "user", "content": qa["question"]})
        messages.append({"role": "assistant", "content": qa["answer"]})

    messages.append({"role": "user", "content": f"Please ask the next {topic} question."})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return response.choices[0].message.content.strip()


# === GPT VOICE ===
def speak_text(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(response.content)
        st.audio(tmpfile.name, format="audio/mp3")


# === AUDIO RECORDER (MIC + WAV EXPORT) ===
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.recorded_frames.append(audio)
        return frame

def record_audio(key):
    st.markdown("🎙️ Please record your answer below using the microphone:")
    ctx = webrtc_streamer(
        key=f"webrtc-{key}",
        mode="sendonly",
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=AudioProcessor,
    )

    audio_path = None
    if ctx.state.playing:
        st.info("⏺️ Recording... Speak now.")
    elif ctx.state.audio_receiver:
        processor = ctx.audio_processor
        if processor and processor.recorded_frames:
            # Save recording
            audio_data = np.concatenate(processor.recorded_frames, axis=0).astype(np.int16)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                sf.write(f.name, audio_data, 48000)
                audio_path = f.name
                st.success("✅ Recording complete!")
    return audio_path


# === TRANSCRIBE AUDIO ===
def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return transcript.text
    except Exception as e:
        st.error(f"❌ Transcription error: {str(e)}")
        return None
