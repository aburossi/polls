import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define static questions and answers
questions = [
    "What is the capital of France?",
    "What is 2 + 2?",
    "Which is the largest planet?"
]

options = ["A", "B", "C", "D"]

# Initialize Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("Umfrage")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

# Function to add responses to the Google Sheet
def add_responses_to_sheet(responses):
    rows = [[question, answer] for question, answer in responses.items()]
    worksheet.append_rows(rows)

# Function to get all responses from the Google Sheet
def get_all_responses():
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

# Initialize session state
if "responses" not in st.session_state:
    st.session_state.responses = {q: [] for q in questions}

# Display questions for polling
st.header("Classroom Poll")

responses = {}
for idx, question in enumerate(questions):
    st.write(f"**{question}**")
    response = st.radio("", options, key=f"poll_q_{idx}")
    responses[question] = response

if st.button("Submit Poll"):
    add_responses_to_sheet(responses)
    st.success("Responses submitted successfully!")

# Display results
try:
    all_responses = get_all_responses()
    if not all_responses.empty:
        st.header("Poll Results")
        results_df = pd.DataFrame(all_responses)
        for question in questions:
            st.write(f"**{question}**")
            response_data = results_df[results_df['Question'] == question]['Answer'].value_counts()
            st.bar_chart(response_data)
except Exception as e:
    st.error(f"An error occurred: {e}")

# Debugging: Print all responses
st.write("All responses from the sheet:")
st.write(all_responses)
