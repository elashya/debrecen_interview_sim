# utils.py
import streamlit as st
import openai
import tempfile
import base64
import requests
import os

openai.api_key = st.secrets["OPENAI_API_KEY"]

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

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages
    )

    return response.choices[0].message.content.strip()

def speak_text(text):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="shimmer",  # Options: alloy, echo, fable, onyx, nova, shimmer
        input=text
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(response.content)
        st.audio(tmpfile.name, format="audio/mp3")

def record_audio(key):
    audio_bytes = st.audio_recorder("🎙️ Record your answer", key=key)
    if audio_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
            f.write(audio_bytes)
            return f.name
    return None

def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return transcript.text
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

