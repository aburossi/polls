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
    "1. Frage",
    "2. Frage",
    "3. Frage"
]

options = ["A", "B", "C", "D"]

# Initialize Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("Umfrage")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

# Function to add response to the Google Sheet
def add_response_to_sheet(question, answer):
    worksheet.append_row([question, answer])

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
st.header("Umfrage")

if st.session_state.has_submitted:
    st.write("You have already submitted your answers today. Thank you!")
else:
    for idx, question in enumerate(questions):
        st.write(f"**{question}**")
        response = st.radio("", options, key=f"poll_q_{idx}")

        if st.button(f"Antworten für Frage {idx + 1} senden", key=f"submit_q_{idx}"):
            if response:
                add_response_to_sheet(question, response)
                cookies[f"last_submission_q_{idx}"] = datetime.datetime.now().isoformat()
                cookies.save()
                st.success(f"Antwort '{question}' erfolgreich gesendet!")
            else:
                st.error("Please select an option before submitting.")

# Update submission status
if all(cookies.get(f"last_submission_q_{idx}") for idx in range(len(questions))):
    st.session_state.has_submitted = True
    cookies["last_submission"] = datetime.datetime.now().isoformat()
    cookies.save()
