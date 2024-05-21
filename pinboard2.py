import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_cookies_manager import EncryptedCookieManager
import datetime

# Load credentials from Streamlit secrets
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)

# Attempt to open the specific spreadsheet
try:
    spreadsheet = client.open("Pinnwand")  # Replace with your spreadsheet name
    worksheet = spreadsheet.worksheet("Sheet2")  # Replace with your sheet name
except Exception as e:
    st.error(f"Error opening spreadsheet: {e}")

# Check if headers exist and add them if they don't
def ensure_headers():
    headers = worksheet.row_values(1)
    if headers != ["Number", "Answer", "Date", "Time"]:
        worksheet.update('A1', [["Number", "Answer", "Date", "Time"]])

ensure_headers()

# Initialize cookies manager
cookies = EncryptedCookieManager(prefix="pin_", password=credentials_dict["cookie_password"])

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

def add_input_to_sheet(question_number, input_text):
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    worksheet.append_row([question_number, input_text, date, time])

def main():
    st.title("PinBoard - Input")

    if st.session_state.has_submitted:
        st.write("You have already submitted text today. Thank you!")
    else:
        st.header("Deine Antwort")
        question_number = st.number_input("Fragenummer", min_value=1, step=1)
        user_input = st.text_area("Tippe einen kurzen Text ein")

        if st.button("Senden"):
            if user_input.strip() and question_number:
                add_input_to_sheet(question_number, user_input)
                cookies["last_submission"] = datetime.datetime.now().isoformat()
                cookies.save()
                st.session_state.has_submitted = True
                st.success("Text hinzugefügt!")
            else:
                st.error("Bitte geben Sie eine Fragenummer und einen Text ein")

if __name__ == "__main__":
    main()
