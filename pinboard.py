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
    worksheet = spreadsheet.sheet1
except Exception as e:
    st.error(f"Error opening spreadsheet: {e}")

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

def add_input_to_sheet(input_text):
    worksheet.append_row([input_text])

def get_all_inputs():
    return worksheet.col_values(1)

def main():
    st.title("PinBoard")

    if st.session_state.has_submitted:
        st.write("You have already submitted text today. Thank you!")
    else:
        st.header("Dein Text")
        user_input = st.text_area("Tippe einen kurzen Text ein")

        if st.button("Senden"):
            if user_input.strip():
                add_input_to_sheet(user_input)
                cookies["last_submission"] = datetime.datetime.now().isoformat()
                cookies.save()
                st.session_state.has_submitted = True
                st.success("Text hinzugefügt!")
            else:
                st.error("Please enter some text")

    st.header("🧾")

    all_inputs = get_all_inputs()
    if all_inputs:
        for input_text in all_inputs:
            st.markdown(f"> {input_text}")
            st.markdown("<hr>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()