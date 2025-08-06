# app.py
import streamlit as st
from interview_logic import run_interview
from feedback import generate_feedback

# === Password protection ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Debrecen Interview Simulator", layout="centered")
    st.title("🔐 Secure Access")
    password = st.text_input("Enter app password:", type="password")

    if password == st.secrets["APP_PIN"]:
        st.session_state.authenticated = True
        st.success("✅ Access granted. Loading app...")
        st.rerun()  # ✅ Force reload to continue
    elif password:
        st.error("❌ Incorrect password. Please try again.")

    st.stop()

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

# === Interview Start ===
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if not st.session_state.interview_started:
    if st.button("🎤 Start Interview"):
        st.session_state.interview_started = True
        st.success("✅ Interview starting... Please wait.")
        st.rerun()
else:
    run_interview()

    # === Show final feedback ===
    if st.session_state.get("interview_done"):
        generate_feedback(st.session_state.qa_history)

        # === Try Again Button ===
        st.markdown("---")
        if st.button("🔁 Try Again"):
            for key in ["interview_started", "question_index", "qa_history", "current_topic", "interview_done", "authenticated"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
