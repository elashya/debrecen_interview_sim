# utils.py
import streamlit as st
from openai import OpenAI
import tempfile
import os

# ✅ Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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


def record_audio(key):
    st.markdown("🎙️ Please record your answer using your phone or computer and upload it below:")
    audio_file = st.file_uploader("Upload your voice answer (MP3 or WebM)", type=["mp3", "webm"], key=key)
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as f:
            f.write(audio_file.read())
            return f.name
    return None


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
