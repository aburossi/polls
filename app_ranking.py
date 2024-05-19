import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from streamlit_cookies_manager import EncryptedCookieManager

def main():
    # Define the choices for the polls
    choices_poll_1 = ["Option A", "Option B", "Option C", "Option D"]
    choices_poll_2 = ["Option A", "Option B", "Option C", "Option D"]
    choices_poll_3 = ["Option A", "Option B", "Option C", "Option D"]

    # Load credentials from Streamlit secrets
    credentials_dict = st.secrets["google_credentials"]

    # Initialize Google Sheets client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("Rankings")  # Replace with your spreadsheet name
    worksheet_poll_1 = spreadsheet.worksheet("Umfrage 1")
    worksheet_poll_2 = spreadsheet.worksheet("Umfrage 2")
    worksheet_poll_3 = spreadsheet.worksheet("Umfrage 3")

    # Check if headers are already present for the polls; if not, add them
    if worksheet_poll_1.row_count == 0:
        worksheet_poll_1.append_row(["Rank", "Choice"])
    if worksheet_poll_2.row_count == 0:
        worksheet_poll_2.append_row(["Rank", "Choice"])
    if worksheet_poll_3.row_count == 0:
        worksheet_poll_3.append_row(["Rank", "Choice"])

    # Initialize cookies manager
    cookies = EncryptedCookieManager(prefix="rank_", password=credentials_dict["cookie_password"])

    if not cookies.ready():
        st.stop()

    # Check if the user has submitted each poll in the last 24 hours
    polls = {
        "Umfrage 1": {"worksheet": worksheet_poll_1, "choices": choices_poll_1, "cookie_key": "last_submission_poll_1"},
        "Umfrage 2": {"worksheet": worksheet_poll_2, "choices": choices_poll_2, "cookie_key": "last_submission_poll_2"},
        "Umfrage 3": {"worksheet": worksheet_poll_3, "choices": choices_poll_3, "cookie_key": "last_submission_poll_3"}
    }

    for poll_name, poll_data in polls.items():
        last_submission = cookies.get(poll_data["cookie_key"])
        if last_submission:
            last_submission_time = datetime.datetime.fromisoformat(last_submission)
            if (datetime.datetime.now() - last_submission_time).days < 1:
                poll_data["has_submitted"] = True
            else:
                poll_data["has_submitted"] = False
        else:
            poll_data["has_submitted"] = False

    st.title("Ordnen Sie die folgenden Optionen nach Ihrer Präferenz:")

    # Function to create ranking selectors and handle submissions
    def create_ranking_poll(choices, worksheet, poll_name, cookie_key):
        rankings = {}
        for i in range(1, len(choices) + 1):
            available_choices = [choice for choice in choices if choice not in rankings.values()]
            rankings[i] = st.selectbox(f"{poll_name} - Rank {i}", available_choices, key=f"{poll_name}_{i}")

        # Function to add rankings to the Google Sheet
        def add_rankings_to_sheet(rankings):
            rows = [[rank, choice] for rank, choice in rankings.items()]
            worksheet.append_rows(rows)

        if st.button(f"Präferenzen {poll_name} senden"):
            add_rankings_to_sheet(rankings)
            cookies[cookie_key] = datetime.datetime.now().isoformat()
            cookies.save()
            st.success(f"{poll_name} Präferenzen erfolgreich gesendet!")

    # Create ranking polls
    for poll_name, poll_data in polls.items():
        if poll_data["has_submitted"]:
            st.write(f"Sie haben bereits Ihre Präferenzen für {poll_name} abgegeben. Bitte warten Sie bis zur nächsten Umfrage.")
        else:
            create_ranking_poll(poll_data["choices"], poll_data["worksheet"], poll_name, poll_data["cookie_key"])

if __name__ == "__main__":
    main()
