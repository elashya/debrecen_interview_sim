# feedback.py
import streamlit as st
import openai
from utils import speak_text

openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_feedback(qa_history):
    if not qa_history:
        st.warning("No answers found to evaluate.")
        return

    # === Build GPT feedback prompt ===
    system_prompt = """You are an admissions interviewer for the University of Debrecen.
The student just completed a voice-based entrance interview (personal, biology, chemistry).
Now, provide a thoughtful summary evaluating their:

- Answer accuracy
- Confidence and tone
- Clarity of communication
- Understanding of biology/chemistry
- Motivation to study at Debrecen

Give final feedback on:
- Strengths
- Areas to improve
- Final score (out of 10)
- Likelihood of acceptance (e.g. high, medium, low)

Keep tone supportive but honest. Avoid repetition."""

    messages = [{"role": "system", "content": system_prompt}]

    for qa in qa_history:
        messages.append({"role": "user", "content": f"Question: {qa['question']}"})
        messages.append({"role": "assistant", "content": f"Answer: {qa['answer']}"})

    messages.append({"role": "user", "content": "Please give the final feedback now."})

    # === Get GPT feedback ===
    with st.spinner("🔍 Evaluating interview..."):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

    feedback_text = response.choices[0].message.content.strip()

    # === Display + Speak it ===
    st.markdown("## 🧾 Final Interview Feedback")
    st.markdown(feedback_text)
    st.markdown("🎧 Voice summary below:")

    speak_text(feedback_text)

