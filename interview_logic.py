# interview_logic.py
import streamlit as st
import streamlit.components.v1 as components
from utils import speak_text, record_audio, transcribe_audio, ask_gpt_question

def run_interview():
    # === Initialize session state ===
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
        st.session_state.current_topic = "personal"
        st.session_state.question_index = 1

    qa = st.session_state.qa_history
    current_topic = st.session_state.current_topic
    total_answered = len(qa)
    total_expected = 8  # 2 personal, 3 biology, 3 chemistry
    percent_complete = int((total_answered / total_expected) * 100)

    # === Show progress tracker ===
    with st.container():
        st.markdown("### 📊 Interview Progress")
        st.progress(percent_complete)
        st.markdown(f"- ✅ **Answered:** {total_answered} / {total_expected}")
        st.markdown(f"- 🧪 **Current Topic:** `{current_topic.capitalize()}`")

        if total_answered > 0:
            st.markdown("- 🧠 **Estimated Score:** 🔄 Estimating… *(Final score at the end)*")

    # === Auto-scroll anchor ===
    st.markdown("<a name='question-area'></a>", unsafe_allow_html=True)

    st.markdown(f"### ❓ Question {st.session_state.question_index}")

    # === Ask GPT for next question ===
    question = ask_gpt_question(
        history=qa,
        topic=current_topic
    )

    # === Speak the question ===
    speak_text(question)

    # === Record user answer ===
    audio_file = record_audio(key=f"audio_{st.session_state.question_index}")

    if audio_file:
        user_answer = transcribe_audio(audio_file)

        if user_answer:
            st.markdown(f"🗣️ **Your Answer:** {user_answer}")

            # === Save the Q&A ===
            qa.append({
                "question": question,
                "answer": user_answer,
                "topic": current_topic
            })

            # === Topic transition logic ===
            topic_count = len([q for q in qa if q['topic'] == current_topic])

            if current_topic == "personal" and topic_count >= 2:
                st.session_state.current_topic = "biology"
            elif current_topic == "biology" and topic_count >= 3:
                st.session_state.current_topic = "chemistry"
            elif current_topic == "chemistry" and topic_count >= 3:
                st.success("✅ Interview completed!")
                st.session_state.interview_done = True
                return

            # === Next Question button + scroll logic ===
            if st.button("➡️ Next Question"):
                st.session_state.question_index += 1

                components.html("""
                    <script>
                        window.location.href = "#question-area";
                    </script>
                """, height=0)

                st.rerun()

