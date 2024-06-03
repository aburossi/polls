import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Constants
SPREADSHEET_NAME = "Umfrage"  # Replace with your spreadsheet name
QUESTIONS = [
    "1. Frage",
    "2. Frage",
    "3. Frage"
]
OPTIONS = ["Select an option", "A", "B", "C", "D"]

# Function to get Google Sheets client
def get_gspread_client():
    credentials_dict = st.secrets["google_credentials"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict, 
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(credentials)

# Function to get worksheet
def get_worksheet(client, sheet_name):
    try:
        spreadsheet = client.open(sheet_name)
        return spreadsheet.sheet1
    except gspread.SpreadsheetNotFound:
        st.error("Spreadsheet not found. Please check the name and try again.")
        return None

# Function to add response to Google Sheets
def add_response_to_sheet(worksheet, question, answer):
    try:
        worksheet.append_row([question, answer])
    except Exception as e:
        st.error(f"Failed to add response: {e}")

# Main function
def main():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://raw.githubusercontent.com/aburossi/polls/main/background.jpg');
            background-size: cover;
        }
        .submitted {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: black;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0

    if 'responses' not in st.session_state:
        st.session_state.responses = {}

    client = get_gspread_client()
    worksheet = get_worksheet(client, SPREADSHEET_NAME)

    if worksheet:
        if st.session_state.current_question < len(QUESTIONS):
            question = QUESTIONS[st.session_state.current_question]
            st.write(f"**{question}**")
            response = st.selectbox("", OPTIONS, key=f"poll_q_{st.session_state.current_question}")
            
            if st.button("Submit response"):
                if response != "Select an option":
                    st.session_state.responses[question] = response
                    add_response_to_sheet(worksheet, question, response)
                    st.session_state.current_question += 1
                    st.experimental_rerun()  # Rerun to load the next question
                else:
                    st.error("Please select an option before submitting.")
        else:
            st.session_state.has_submitted = True
            st.markdown('<div class="submitted"><h2>Vielen Dank für Ihre Antworten!</h2></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
