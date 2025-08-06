# app.py
import streamlit as st
from interview_logic import run_interview

st.set_page_config(page_title="Debrecen Interview Simulator", layout="centered")
st.title("🎓 Debrecen Interview Simulator")

st.markdown("""
Simulate your entrance interview for the **University of Debrecen**.
Answer by voice — you'll receive voice + text feedback at the end.
""")

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if not st.session_state.interview_started:
    if st.button("🎤 Start Interview"):
        st.session_state.interview_started = True
        st.experimental_rerun()
else:
    run_interview()

    # ✅ Add this block:
    if st.session_state.get("interview_done"):
        from feedback import generate_feedback
        generate_feedback(st.session_state.qa_history)
