import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_cookies_manager import EncryptedCookieManager
import datetime

# Load credentials from Streamlit secrets
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)
spreadsheet = client.open("WordCloudInputs")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

# Initialize cookies manager
cookies = EncryptedCookieManager(prefix="wc_", password=credentials_dict["cookie_password"])

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

def add_input_to_sheet(input_text):
    worksheet.append_row([input_text])

def main():
    st.title("Word Cloud Input")

    if st.session_state.has_submitted:
        st.write("You have already submitted text today. Thank you!")
    else:
        st.header("Input Text")
        user_input = st.text_area("Enter the text for the word cloud")

        if st.button("Submit"):
            if user_input.strip():
                add_input_to_sheet(user_input)
                cookies["last_submission"] = datetime.datetime.now().isoformat()
                cookies.save()
                st.session_state.has_submitted = True
                st.success("Text added!")
            else:
                st.error("Please enter some text")

if __name__ == "__main__":
    main()
