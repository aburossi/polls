import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from streamlit_cookies_manager import EncryptedCookieManager

# Constants
SPREADSHEET_NAME = "Rankings"  # Replace with your spreadsheet name
CHOICES_POLL_1 = ["Option A", "Option B", "Option C", "Option D"]
CHOICES_POLL_2 = ["Option A", "Option B", "Option C", "Option D"]
CHOICES_POLL_3 = ["Option A", "Option B", "Option C", "Option D"]

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
def create_ranking_poll(choices, worksheet, poll_name, cookie_key, cookies):
    rankings = {}
    for i in range(1, len(choices) + 1):
        available_choices = [choice for choice in choices if choice not in rankings.values()]
        rankings[i] = st.selectbox(f"{poll_name} - Rank {i}", available_choices, key=f"{poll_name}_{i}")

    if st.button(f"Submit {poll_name} Preferences"):
        add_rankings_to_sheet(worksheet, rankings)
        cookies[cookie_key] = datetime.datetime.now().isoformat()
        cookies.save()
        st.success(f"{poll_name} preferences successfully submitted!")
        st.session_state.current_page += 1
        st.experimental_rerun()

def main():
    # Initialize Google Sheets client
    client = get_gspread_client()

    # Initialize cookies manager
    credentials_dict = st.secrets["google_credentials"]
    cookies = EncryptedCookieManager(prefix="rank_", password=credentials_dict["cookie_password"])

    if not cookies.ready():
        st.stop()

    # Track the current page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

    # Define the polls
    polls = [
        {"name": "Umfrage 1", "choices": CHOICES_POLL_1, "worksheet": get_worksheet(client, SPREADSHEET_NAME, "Umfrage 1"), "cookie_key": "last_submission_poll_1"},
        {"name": "Umfrage 2", "choices": CHOICES_POLL_2, "worksheet": get_worksheet(client, SPREADSHEET_NAME, "Umfrage 2"), "cookie_key": "last_submission_poll_2"},
        {"name": "Umfrage 3", "choices": CHOICES_POLL_3, "worksheet": get_worksheet(client, SPREADSHEET_NAME, "Umfrage 3"), "cookie_key": "last_submission_poll_3"}
    ]

    # Check if the user has submitted each poll in the last 24 hours
    for poll in polls:
        last_submission = cookies.get(poll["cookie_key"])
        if last_submission:
            last_submission_time = datetime.datetime.fromisoformat(last_submission)
            if (datetime.datetime.now() - last_submission_time).days < 1:
                poll["has_submitted"] = True
            else:
                poll["has_submitted"] = False
        else:
            poll["has_submitted"] = False

    # Display the poll based on the current page
    if st.session_state.current_page < len(polls):
        poll = polls[st.session_state.current_page]
        if poll["has_submitted"]:
            st.write(f"You have already submitted your preferences for {poll['name']}. Please wait until the next survey.")
            st.session_state.current_page += 1
            st.experimental_rerun()
        else:
            st.title(f"Rank the options for {poll['name']}")
            create_ranking_poll(poll["choices"], poll["worksheet"], poll["name"], poll["cookie_key"], cookies)
    else:
        st.write("Thank you for submitting all your rankings!")

if __name__ == "__main__":
    main()
