import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

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

def main():
    st.header("Umfrage")

    # Initialize submission state
    if 'submitted_questions' not in st.session_state:
        st.session_state.submitted_questions = []

    # Collect responses for all questions
    responses = {}
    for idx, question in enumerate(questions):
        st.write(f"**{question}**")
        response = st.radio("", options, key=f"poll_q_{idx}")
        responses[question] = response

    # Submission button for all questions
    if st.button("Submit all responses"):
        all_answered = True
        for question, response in responses.items():
            if not response:
                st.error(f"Please select an option for: {question}")
                all_answered = False
        
        if all_answered:
            for question, response in responses.items():
                add_response_to_sheet(question, response)
            st.session_state.submitted_questions.extend(range(len(questions)))
            st.markdown('<div class="submitted"><h2>Thank you for your submission!</h2></div>', unsafe_allow_html=True)
            st.experimental_rerun()  # Rerun to show the submission thank you message

if __name__ == "__main__":
    main()
