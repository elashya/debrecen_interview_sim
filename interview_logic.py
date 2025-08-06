# interview_logic.py
import streamlit as st
from utils import speak_text, record_audio, transcribe_audio

QUESTIONS = [
    {"type": "personal", "question": "Why do you want to study at the University of Debrecen?"},
    {"type": "personal", "question": "What are your hobbies and interests outside of academics?"},
    {"type": "biology", "question": "What are the main differences between prokaryotic and eukaryotic cells?"},
    {"type": "biology", "question": "Can you describe the function of mitochondria in a cell?"},
    {"type": "biology", "question": "What is osmosis, and why is it important for cells?"},
    {"type": "chemistry", "question": "What is the atomic number and what does it represent?"},
    {"type": "chemistry", "question": "Explain the difference between ionic and covalent bonds."},
    {"type": "chemistry", "question": "What happens during a neutralization reaction?"}
]

def run_interview():
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
        st.session_state.responses = []

    idx = st.session_state.question_index

    if idx >= len(QUESTIONS):
        st.success("✅ Interview completed!")
        st.session_state.interview_done = True
        return

    question = QUESTIONS[idx]["question"]
    st.markdown(f"### ❓ Question {idx+1}: {question}")

    # GPT voice asks the question
    speak_text(question)

    # Record user answer
    audio_file = record_audio(key=f"audio_{idx}")
    if audio_file:
        answer = transcribe_audio(audio_file)
        if answer:
            st.write(f"🗣️ Your Answer: {answer}")
            st.session_state.responses.append({
                "question": question,
                "answer": answer,
                "topic": QUESTIONS[idx]["type"]
            })
            if st.button("➡️ Next Question"):
                st.session_state.question_index += 1
                st.rerun()

