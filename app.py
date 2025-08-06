# app.py
import streamlit as st
from interview_logic import run_interview
from feedback import generate_feedback

# === Page Setup ===
st.set_page_config(page_title="Debrecen Interview Simulator", layout="centered")
st.title("🎓 Debrecen Interview Simulator")

st.markdown("""
Simulate your entrance interview for the **University of Debrecen**.

You'll receive **spoken questions** in three parts:
- 🧍 Personal questions (motivation, interests)
- 🧬 Biology questions (cells, organelles, etc.)
- ⚗️ Chemistry questions (atoms, bonding, reactions)

🎙️ You’ll **respond using your voice**, and receive detailed **text + audio feedback** at the end.
""")

# === State Initialization ===
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

# === Start Button ===
if not st.session_state.interview_started:
    if st.button("🎤 Start Interview"):
        st.session_state.interview_started = True
        st.experimental_rerun()
else:
    # === Run the main interview loop ===
    run_interview()

    # === Show feedback if finished ===
    if st.session_state.get("interview_done"):
        generate_feedback(st.session_state.qa_history)

        # === Try Again Button ===
        st.markdown("---")
        if st.button("🔁 Try Again"):
            for key in ["interview_started", "question_index", "qa_history", "current_topic", "interview_done"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
