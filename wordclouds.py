import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load credentials from Streamlit secrets
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)
spreadsheet = client.open("WordCloudInputs")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

def add_input_to_sheet(input_text):
    worksheet.append_row([input_text])

def main():
    # Add custom CSS for the background image
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://raw.githubusercontent.com/aburossi/polls/main/background.jpg');
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("")

    if 'has_submitted' not in st.session_state:
        st.session_state.has_submitted = False

    if st.session_state.has_submitted:
        st.write("Thank you for your submission!")
    else:
        st.header("Deine Wörter")
        user_input = st.text_area("👇 💬")

        if st.button("Senden"):
            if user_input.strip():
                add_input_to_sheet(user_input)
                st.session_state.has_submitted = True
                st.success("Thank you for your submission!")
            else:
                st.error("Please enter some text")

if __name__ == "__main__":
    main()
