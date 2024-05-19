# poll_app.py
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define static questions and answers
questions = [
    "Frage 1",
    "Frage 2",
    "Frage 3"
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

# Initialize session state
if "has_submitted" not in st.session_state:
    st.session_state.has_submitted = False

# Display questions for polling
st.header("Classroom Poll")

if st.session_state.has_submitted:
    st.write("You have already submitted your answers. Thank you!")
else:
    responses = {}
    for idx, question in enumerate(questions):
        st.write(f"**{question}**")
        response = st.radio("", options, key=f"poll_q_{idx}")
        responses[question] = response

    if st.button("Submit Poll"):
        add_responses_to_sheet(responses)
        st.session_state.has_submitted = True
        st.success("Responses submitted successfully!")

