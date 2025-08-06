# interview_logic.py (GPT-driven)
import streamlit as st
from utils import speak_text, record_audio, transcribe_audio, ask_gpt_question

def run_interview():
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
        st.session_state.current_topic = "personal"  # personal → biology → chemistry
        st.session_state.question_index = 1

    st.markdown(f"### ❓ Question {st.session_state.question_index}")

    # 1. Get GPT-generated question
    question = ask_gpt_question(
        history=st.session_state.qa_history,
        topic=st.session_state.current_topic
    )

    # 2. Speak the question
    speak_text(question)

    # 3. Record the user's voice
    audio_file = record_audio(key=f"audio_{st.session_state.question_index}")
    if audio_file:
        user_answer = transcribe_audio(audio_file)

        if user_answer:
            st.write(f"🗣️ Your Answer: {user_answer}")

            # 4. Save to history
            st.session_state.qa_history.append({
                "question": question,
                "answer": user_answer,
                "topic": st.session_state.current_topic
            })

            # 5. Move to next topic if needed
            count = len([qa for qa in st.session_state.qa_history if qa['topic'] == st.session_state.current_topic])
            if st.session_state.current_topic == "personal" and count >= 2:
                st.session_state.current_topic = "biology"
            elif st.session_state.current_topic == "biology" and count >= 3:
                st.session_state.current_topic = "chemistry"
            elif st.session_state.current_topic == "chemistry" and count >= 3:
                st.success("✅ Interview completed!")
                st.session_state.interview_done = True
                return

            if st.button("➡️ Next Question"):
                st.session_state.question_index += 1
                st.rerun()
