# feedback.py
import streamlit as st
from openai import OpenAI
from utils import speak_text
import tempfile

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_feedback(qa_history):
    if not qa_history:
        st.warning("No answers found to evaluate.")
        return

    # === Group by topic ===
    topic_groups = {"personal": [], "biology": [], "chemistry": []}
    for qa in qa_history:
        topic_groups[qa["topic"]].append(qa)

    # === GPT prompt ===
    messages = [{"role": "system", "content": """You are an entrance interview evaluator for the University of Debrecen.
The student just completed a voice interview. You will:

1. Review all Q&A by topic.
2. Give brief topic-specific feedback.
3. Assign a score per topic:
   - Personal: out of 2
   - Biology: out of 3
   - Chemistry: out of 3
4. Give an overall mark (out of 8) and likelihood of acceptance.

Be supportive but honest. Format output clearly."""}]

    for topic in ["personal", "biology", "chemistry"]:
        qas = topic_groups[topic]
        for qa in qas:
            messages.append({"role": "user", "content": f"{topic.upper()} | Question: {qa['question']}"})
            messages.append({"role": "assistant", "content": f"Answer: {qa['answer']}"})

    messages.append({"role": "user", "content": "Please evaluate and score by topic."})

    # === Call GPT ===
    with st.spinner("🧠 Analyzing your interview..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

    feedback_text = response.choices[0].message.content.strip()

    # === Display feedback ===
    st.markdown("## 🧾 Final Interview Feedback")
    st.markdown(feedback_text)
    speak_text(feedback_text)

    # === Downloadable Transcript ===
    st.markdown("### 📥 Download Full Transcript")

    transcript = "\n".join(
        [f"Q: {qa['question']}\nA: {qa['answer']}\n" for qa in qa_history]
    )
    full_text = f"Interview Transcript\n\n{transcript}\n\nFeedback:\n{feedback_text}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
        f.write(full_text)
        download_path = f.name

    with open(download_path, "rb") as file:
        st.download_button(
            label="⬇️ Download as TXT",
            data=file,
            file_name="debrecen_interview_feedback.txt",
            mime="text/plain"
        )
