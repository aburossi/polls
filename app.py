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

    # Initialize submission state
    if 'has_submitted' not in st.session_state:
        st.session_state.has_submitted = False

    st.header("Umfrage")

    if st.session_state.has_submitted:
        st.markdown('<div class="submitted"><h2>Thank you for your submission!</h2></div>', unsafe_allow_html=True)
    else:
        for idx, question in enumerate(questions):
            st.write(f"**{question}**")
            response = st.radio("", options, key=f"poll_q_{idx}")

            if st.button(f"Antworten für Frage {idx + 1} senden", key=f"submit_q_{idx}"):
                if response:
                    add_response_to_sheet(question, response)
                    if 'submitted_questions' not in st.session_state:
                        st.session_state.submitted_questions = set()
                    st.session_state.submitted_questions.add(idx)
                    st.success(f"Antwort '{question}' erfolgreich gesendet!")
                else:
                    st.error("Please select an option before submitting.")

        # Update submission status if all questions have been answered
        if len(st.session_state.get('submitted_questions', set())) == len(questions):
            st.session_state.has_submitted = True
            st.experimental_rerun()

if __name__ == "__main__":
    main()
