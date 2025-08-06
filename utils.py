# core_utils.py
import streamlit as st
from openai import OpenAI
import tempfile
import os
from pydub import AudioSegment

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
        st.audio(tmpfile.name, format="audio/mp3")

# === FILE-UPLOAD ONLY AUDIO HANDLER ===
def record_audio(key):
    st.markdown("📁 Upload your recorded voice answer:")

    uploaded = st.file_uploader(
        "Accepted formats: MP3, WAV, M4A, AMR, WEBM",
        type=["mp3", "wav", "webm", "m4a", "amr"],
        key=f"upload-{key}"
    )

    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded.name.split('.')[-1]}") as f:
            f.write(uploaded.read())
            return f.name
    return None

# === TRANSCRIBE AUDIO (AMR → WAV using pydub) ===
def transcribe_audio(audio_path):
    try:
        ext = os.path.splitext(audio_path)[-1].lower()

        if ext == ".amr":
            converted_path = audio_path.replace(".amr", ".wav")
            sound = AudioSegment.from_file(audio_path, format="amr")
            sound.export(converted_path, format="wav")
            audio_path = converted_path

        with open(audio_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return transcript.text
    except Exception as e:
        st.error(f"❌ Transcription error: {str(e)}")
        return None
