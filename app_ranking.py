import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Constants
SPREADSHEET_NAME = "Rankings"  # Replace with your spreadsheet name
CHOICES_POLL_1 = ["Option A", "Option B", "Option C", "Option D"]
CHOICES_POLL_2 = ["Option A", "Option B", "Option C", "Option D"]

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
    spreadsheet = client.open(sheet_name)
    worksheet = spreadsheet.worksheet(worksheet_name)
    if worksheet.row_count == 0:
        worksheet.append_row(["Rank", "Choice"])
    return worksheet

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

    if st.button(f"Submit {poll_name} Preferences"):
        add_rankings_to_sheet(worksheet, rankings)
        st.success(f"{poll_name} preferences successfully submitted!")
        st.session_state.current_page += 1
        st.experimental_rerun()

def main():
    # Initialize Google Sheets client
    client = get_gspread_client()

    # Track the current page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

    # Define the polls
    polls = [
        {"name": "Umfrage 1", "choices": CHOICES_POLL_1, "worksheet": get_worksheet(client, SPREADSHEET_NAME, "Umfrage 1")},
        {"name": "Umfrage 2", "choices": CHOICES_POLL_2, "worksheet": get_worksheet(client, SPREADSHEET_NAME, "Umfrage 2")},
    ]

    # Display the poll based on the current page
    if st.session_state.current_page < len(polls):
        poll = polls[st.session_state.current_page]
        st.title(f"Ordnen Sie die Optionen für {poll['name']}")
        create_ranking_poll(poll["choices"], poll["worksheet"], poll["name"])
    else:
        st.write("Vielen Dank für Ihre Antworten!")

if __name__ == "__main__":
    main()
