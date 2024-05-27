import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load credentials from Streamlit secrets
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)
spreadsheet = client.open("Umfrage")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

questions = [
    "1. Frage",
    "2. Frage",
    "3. Frage"
]

options = ["Select an option", "A", "B", "C", "D"]

def add_response_to_sheet(question, answer):
    worksheet.append_row([question, answer])

def main():
    # Add custom CSS for the background image
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

    if 'has_submitted' not in st.session_state:
        st.session_state.has_submitted = False

    if st.session_state.has_submitted:
        st.markdown('<div class="submitted"><h2>Vielen Dank!</h2></div>', unsafe_allow_html=True)
    else:
        st.header("Umfrage")

        # Collect responses for all questions
        responses = {}
        for idx, question in enumerate(questions):
            st.write(f"**{question}**")
            response = st.selectbox("", options, key=f"poll_q_{idx}")
            responses[question] = response if response != "Select an option" else ""

        # Submission button for all questions
        if st.button("Submit all responses"):
            for question, response in responses.items():
                add_response_to_sheet(question, response)
            st.session_state.has_submitted = True
            st.experimental_rerun()  # Rerun to show the submission thank you message

if __name__ == "__main__":
    main()
