import streamlit as st
import pandas as pd

# Define static questions and answers
questions = [
    "What is the capital of France?",
    "What is 2 + 2?",
    "Which is the largest planet?"
]

options = ["A", "B", "C", "D"]

# Initialize session state
if "responses" not in st.session_state:
    st.session_state.responses = {q: [] for q in questions}

# Display questions for polling
st.header("Classroom Poll")

responses = []
for idx, question in enumerate(questions):
    st.write(f"**{question}**")
    response = st.radio("", options, key=f"poll_q_{idx}")
    responses.append(response)

if st.button("Submit Poll"):
    for idx, response in enumerate(responses):
        st.session_state.responses[questions[idx]].append(response)
    st.success("Responses submitted successfully!")

# Display results
if any(st.session_state.responses[q] for q in questions):
    st.header("Poll Results")
    for question in questions:
        st.write(f"**{question}**")
        response_data = pd.Series(st.session_state.responses[question]).value_counts()
        st.bar_chart(response_data)
