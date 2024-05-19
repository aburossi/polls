import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# Load credentials from Streamlit secrets
credentials_dict = st.secrets["google_credentials"]

# Define static questions and answers
questions = [
    "What is the capital of France?",
    "What is 2 + 2?",
    "Which is the largest planet?"
]

options = ["A", "B", "C", "D"]

# Initialize Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("Umfrage")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

# Function to add responses to the Google Sheet
def add_responses_to_sheet(responses):
    rows = [[question, answer] for question, answer in responses.items()]
    worksheet.append_rows(rows)

# Initialize cookies manager
cookies = EncryptedCookieManager(prefix="poll_", password=credentials_dict["cookie_password"])

if not cookies.ready():
    st.stop()

# Check if the user has submitted in the last 24 hours
last_submission = cookies.get("last_submission")
if last_submission:
    last_submission_time = datetime.datetime.fromisoformat(last_submission)
    if (datetime.datetime.now() - last_submission_time).days < 1:
        st.session_state.has_submitted = True
else:
    st.session_state.has_submitted = False

# Display questions for polling
st.header("Classroom Poll")

if st.session_state.has_submitted:
    st.write("You have already submitted your answers today. Thank you!")
else:
    responses = {}
    for idx, question in enumerate(questions):
        st.write(f"**{question}**")
        response = st.radio("", options, key=f"poll_q_{idx}")
        responses[question] = response

    if st.button("Submit Poll"):
        add_responses_to_sheet(responses)
        cookies["last_submission"] = datetime.datetime.now().isoformat()
        cookies.save()
        st.session_state.has_submitted = True
        st.success("Responses submitted successfully!")
