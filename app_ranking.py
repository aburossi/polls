import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Constants
SPREADSHEET_NAME = "Rankings"  # Replace with your spreadsheet name
QUESTION_SHEET_NAME = "QandA"  # Sheet name where questions and answers are stored

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
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Worksheet '{worksheet_name}' not found in the spreadsheet '{sheet_name}'.")
        return None

# Function to get questions and answers from Google Sheets
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def get_questions_and_answers():
    client = get_gspread_client()
    worksheet = get_worksheet(client, SPREADSHEET_NAME, QUESTION_SHEET_NAME)
    if worksheet:
        questions_and_answers = worksheet.get_all_values()
        # Transpose the data to get questions in columns
        questions_and_answers = list(zip(*questions_and_answers))
        return questions_and_answers
    return []

# Function to add rankings to the Google Sheet
def add_rankings_to_sheet(worksheet, rankings):
    rows = [[rank, choice] for rank, choice in rankings.items()]
    worksheet.append_rows(rows)

# Function to create ranking selectors and handle submissions
def create_ranking_poll(choices, worksheet, poll_name):
    rankings = {}
    for i in range(1, len(choices) + 1):
        available_choices = [choice for choice in choices if choice not in rankings.values()]
        rankings[i] = st.selectbox(f"Rangordnung {i}", available_choices, key=f"{poll_name}_{i}")

    if st.button(f"Submi {poll_name} Preferences"):
        add_rankings_to_sheet(worksheet, rankings)
        st.success(f"{poll_name} preferences successfully submitted!")
        st.session_state["current_page"] += 1
        st.experimental_rerun()

def main():
    # Initialize Google Sheets client
    client = get_gspread_client()

    # Track the current page in session state
    if 'current_page' not in st.session_state:
        st.session_state["current_page"] = 0

    # Load questions and answers from Google Sheets
    questions_and_answers = get_questions_and_answers()

    # Create a poll for each question
    polls = []
    for q_a in questions_and_answers:
        question = q_a[0]
        answers = q_a[1:]
        worksheet = get_worksheet(client, SPREADSHEET_NAME, question)
        if worksheet:
            polls.append({"name": question, "choices": answers, "worksheet": worksheet})

    # Display the poll based on the current page
    if st.session_state["current_page"] < len(polls):
        poll = polls[st.session_state["current_page"]]
        st.title(f"Ordnen Sie die Optionen für {poll['name']}")
        create_ranking_poll(poll["choices"], poll["worksheet"], poll["name"])
    else:
        st.write("Vielen Dank für Ihre Antworten!")

if __name__ == "__main__":
    main()
