# app.py
import streamlit as st
from interview_logic import run_interview
from feedback import generate_feedback

st.set_page_config(page_title="Debrecen Interview Simulator", layout="centered")

st.title("🎓 Debrecen Interview Simulator")
st.markdown("""
Simulate your entrance interview for the **University of Debrecen**.
This includes **personal**, **biology**, and **chemistry** questions.
You’ll answer using your voice, and receive voice-based feedback at the end.
""")

# Step-by-step control
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if not st.session_state.interview_started:
    if st.button("🎤 Start Interview"):
        st.session_state.interview_started = True
        st.experimental_rerun()
else:
    run_interview()  # Import from separate file

