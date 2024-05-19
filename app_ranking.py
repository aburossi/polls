import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from streamlit_cookies_manager import EncryptedCookieManager

def main():
    # Define the choices for both polls
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

    # Check if headers are already present for both polls; if not, add them
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

    # Check if the user has submitted in the last 24 hours
    last_submission = cookies.get("last_submission")
    if last_submission:
        last_submission_time = datetime.datetime.fromisoformat(last_submission)
        if (datetime.datetime.now() - last_submission_time).days < 1:
            st.session_state.has_submitted = True
    else:
        st.session_state.has_submitted = False

    st.title("Ordnen Sie die folgenden Optionen nach Ihrer Präferenz:")

    if st.session_state.has_submitted:
        st.write("Sie haben bereits Ihre Präferenzen abgegeben. Bitte warten Sie bis zur nächsten Umfrage.")
    else:
        # Function to create ranking selectors and handle submissions
        def create_ranking_poll(choices, worksheet, poll_name):
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
                cookies["last_submission"] = datetime.datetime.now().isoformat()
                cookies.save()
                st.session_state.has_submitted = True
                st.success(f"{poll_name} Präferenzen erfolgreich gesendet!")

        # Create ranking polls
        create_ranking_poll(choices_poll_1, worksheet_poll_1, "Poll 1")
        create_ranking_poll(choices_poll_2, worksheet_poll_2, "Poll 2")
        create_ranking_poll(choices_poll_3, worksheet_poll_3, "Poll 3")

if __name__ == "__main__":
    main()
