# interview_logic.py
import streamlit as st
import streamlit.components.v1 as components
from utils import speak_text, record_audio, transcribe_audio, ask_gpt_question

def run_interview():
    # === Initialize session states ===
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
        st.session_state.current_topic = "personal"  # progresses: personal → biology → chemistry
        st.session_state.question_index = 1

    idx = st.session_state.question_index

    # === Auto-scroll anchor ===
    st.markdown("<a name='question-area'></a>", unsafe_allow_html=True)

    st.markdown(f"### ❓ Question {idx}")

    # === Ask GPT to generate the next question based on context ===
    question = ask_gpt_question(
        history=st.session_state.qa_history,
        topic=st.session_state.current_topic
    )

    # === Speak the question ===
    speak_text(question)

    # === Record the user's voice ===
    audio_file = record_audio(key=f"audio_{idx}")

    if audio_file:
        # === Transcribe using Whisper ===
        user_answer = transcribe_audio(audio_file)

        if user_answer:
            st.markdown(f"🗣️ **Your Answer:** {user_answer}")

            # === Save this interaction ===
            st.session_state.qa_history.append({
                "question": question,
                "answer": user_answer,
                "topic": st.session_state.current_topic
            })

            # === Determine whether to switch topic ===
            current_topic_count = len([
                q for q in st.session_state.qa_history
                if q["topic"] == st.session_state.current_topic
            ])

            if st.session_state.current_topic == "personal" and current_topic_count >= 2:
                st.session_state.current_topic = "biology"
            elif st.session_state.current_topic == "biology" and current_topic_count >= 3:
                st.session_state.current_topic = "chemistry"
            elif st.session_state.current_topic == "chemistry" and current_topic_count >= 3:
                st.success("✅ Interview completed!")
                st.session_state.interview_done = True
                return

            # === Button to move to next question ===
            if st.button("➡️ Next Question"):
                st.session_state.question_index += 1

                # === Scroll to question anchor ===
                components.html("""
                    <script>
                        window.location.href = "#question-area";
                    </script>
                """, height=0)

                st.rerun()
