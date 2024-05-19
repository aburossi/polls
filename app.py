import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

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

# Function to set a cookie with the current timestamp
def set_cookie(key, value):
    st.experimental_set_query_params(**{key: value})

# Function to get a cookie value
def get_cookie(key):
    params = st.experimental_get_query_params()
    return params.get(key, [None])[0]

# Initialize session state
if "has_submitted" not in st.session_state:
    st.session_state.has_submitted = False

# Check if the user has submitted in the last 24 hours
last_submission = get_cookie("last_submission")
if last_submission:
    last_submission_time = datetime.datetime.fromisoformat(last_submission)
    if (datetime.datetime.now() - last_submission_time).days < 1:
        st.session_state.has_submitted = True

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
        set_cookie("last_submission", datetime.datetime.now().isoformat())
        st.session_state.has_submitted = True
        st.success("Responses submitted successfully!")
