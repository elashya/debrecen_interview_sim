# core_utils.py
import streamlit as st
from openai import OpenAI
import tempfile
import os
import numpy as np
import soundfile as sf
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import time

# ✅ OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === GPT QUESTION GENERATION ===
def ask_gpt_question(history, topic):
    messages = [
        {"role": "system", "content": f"""You are conducting a University of Debrecen entrance interview.
Ask ONE question at a time in a calm, formal tone.
Current topic: {topic}.
Keep it clear and spoken-friendly. The student answers by voice. Total ~8 questions: 2 personal, 3 biology, 3 chemistry.
Avoid repeating previous questions."""}
    ]

    for qa in history:
        messages.append({"role": "user", "content": f"{qa['question']}"})
        messages.append({"role": "assistant", "content": f"{qa['answer']}"})

    messages.append({"role": "user", "content": f"Please ask the next {topic} question."})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return response.choices[0].message.content.strip()

# === TEXT TO SPEECH ===
def speak_text(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(response.content)
        tmpfile_path = tmpfile.name

    st.audio(tmpfile_path, format="audio/mp3")

# === AUDIO PROCESSOR CLASS ===
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.recorded_frames.append(audio)
        return frame

# === AUDIO RECORDER WITH FALLBACK ===
def record_audio(key):
    st.markdown("🎙️ Please record your answer using the microphone below:")

    rtc_config = {
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }

    ctx = webrtc_streamer(
        key=f"webrtc-{key}",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=rtc_config,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        audio_processor_factory=AudioProcessor,
    )

    audio_path = None
    timeout_seconds = 10

    if ctx.state.playing:
        st.info("⏺️ Recording... Speak now.")

        start_time = time.time()
        while ctx.audio_receiver is None and time.time() - start_time < timeout_seconds:
            time.sleep(0.2)

    if ctx.audio_receiver:
        processor = ctx.audio_processor
        if processor and processor.recorded_frames:
            audio_data = np.concatenate(processor.recorded_frames, axis=0).astype(np.int16)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                sf.write(f.name, audio_data, 48000)
                audio_path = f.name
                st.success("✅ Recording complete!")
                return audio_path

    # === Fallback: File Upload ===
    st.warning("🎤 Recording failed or unavailable. Please upload your answer.")
    uploaded = st.file_uploader("📁 Upload your voice answer (MP3/WAV/WebM)", type=["mp3", "wav", "webm"], key=f"fallback-{key}")
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded.name.split('.')[-1]}") as f:
            f.write(uploaded.read())
            return f.name

    return None

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
