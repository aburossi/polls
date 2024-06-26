import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Constants
SPREADSHEET_NAME = "Umfrage"  # The name of the spreadsheet
ANSWER_SHEET_NAME = "sheet1"  # The sheet where the answers should be saved
QUESTION_SHEET_NAME = "QandA"  # The sheet where questions and answers are stored

# Function to get Google Sheets client
def get_gspread_client():
    credentials_dict = st.secrets["google_credentials"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict, 
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(credentials)

# Function to get worksheet
def get_worksheet(client, sheet_name, worksheet_name):
    try:
        spreadsheet = client.open(sheet_name)
        return spreadsheet.worksheet(worksheet_name)
    except gspread.SpreadsheetNotFound:
        st.error(f"Spreadsheet '{sheet_name}' not found. Please check the name and try again.")
        return None
    except gspread.WorksheetNotFound:
        st.error(f"Worksheet '{worksheet_name}' not found in the spreadsheet '{sheet_name}'.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to check and add headers if missing
def check_and_add_headers(worksheet):
    try:
        headers = worksheet.row_values(1)  # Get the first row (headers)
        if not headers or headers[0] != "Question" or headers[1] != "Answer":
            worksheet.insert_row(["Question", "Answer"], 1)
    except Exception as e:
        st.error(f"Failed to check or add headers: {e}")

# Function to add response to Google Sheets
def add_response_to_sheet(worksheet, question, answer):
    try:
        check_and_add_headers(worksheet)
        worksheet.append_row([question, answer])
    except Exception as e:
        st.error(f"Failed to add response: {e}")

# Function to get questions and answers from Google Sheets
@st.cache_data(ttl=120)  # Cache data for 2 minutes
def get_questions_and_answers():
    client = get_gspread_client()
    worksheet = get_worksheet(client, SPREADSHEET_NAME, QUESTION_SHEET_NAME)
    if worksheet:
        data = worksheet.get_all_values()
        # Transpose data to handle columns as questions and rows as answers
        questions_and_answers = list(zip(*data))
        return questions_and_answers
    return []

# Main function
def main():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0

    if 'responses' not in st.session_state:
        st.session_state.responses = {}

    questions_and_answers = get_questions_and_answers()
    client = get_gspread_client()
    answer_worksheet = get_worksheet(client, SPREADSHEET_NAME, ANSWER_SHEET_NAME)

    if answer_worksheet and questions_and_answers:
        if st.session_state.current_question < len(questions_and_answers):
            question_row = questions_and_answers[st.session_state.current_question]
            question = question_row[0]
            options = [option for option in question_row[1:] if option]  # Filter out empty options
            st.write(f"**{question}**")
            response = st.radio("Select an option:", options, key=f"poll_q_{st.session_state.current_question}")

            if st.button("Submit response"):
                if response:
                    st.session_state.responses[question] = response
                    add_response_to_sheet(answer_worksheet, question, response)
                    st.session_state.current_question += 1
                    st.experimental_rerun()  # Rerun to load the next question
                else:
                    st.error("Please select an option before submitting.")
        else:
            st.session_state.has_submitted = True
            st.markdown('<div class="submitted"><h2>Vielen Dank für Ihre Antworten!</h2></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
