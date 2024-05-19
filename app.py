import streamlit as st
import pandas as pd

def initialize_state():
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "responses" not in st.session_state:
        st.session_state.responses = []

def add_question():
    st.session_state.questions.append({
        "question": st.session_state.question_text,
        "options": [
            st.session_state.option1,
            st.session_state.option2,
            st.session_state.option3,
            st.session_state.option4
        ]
    })
    st.session_state.question_text = ""
    st.session_state.option1 = ""
    st.session_state.option2 = ""
    st.session_state.option3 = ""
    st.session_state.option4 = ""

# Initialize session state
initialize_state()

# User interface to add questions
st.sidebar.header("Add Poll Questions")
st.sidebar.text_input("Question", key="question_text")
st.sidebar.text_input("Option 1", key="option1")
st.sidebar.text_input("Option 2", key="option2")
st.sidebar.text_input("Option 3", key="option3")
st.sidebar.text_input("Option 4", key="option4")
st.sidebar.button("Add Question", on_click=add_question)

# Display questions for polling
if st.session_state.questions:
    st.header("Classroom Poll")

    responses = []
    for idx, q in enumerate(st.session_state.questions):
        st.write(f"**{q['question']}**")
        response = st.radio("", q['options'], key=f"poll_q_{idx}")
        responses.append(response)

    if st.button("Submit Poll"):
        for idx, response in enumerate(responses):
            st.session_state.responses.append({
                "question": st.session_state.questions[idx]['question'],
                "answer": response
            })
        st.success("Responses submitted successfully!")

# Display results
if st.session_state.responses:
    st.header("Poll Results")
    results_df = pd.DataFrame(st.session_state.responses)
    for question in results_df['question'].unique():
        st.write(f"**{question}**")
        response_data = results_df[results_df['question'] == question]['answer'].value_counts()
        st.bar_chart(response_data)
