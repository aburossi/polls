import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

def get_all_entries():
    return worksheet.get_all_records()

def main():
    st.title("🧾 PinBoard Entries")

    st.header("Alle Antworten")

    all_entries = get_all_entries()
    if all_entries:
        for entry in all_entries:
            question_number = entry.get("Number", "Keine Nummer")
            answer_text = entry.get("Answer", "Keine Antwort")
            date = entry.get("Date", "Kein Datum")
            time = entry.get("Time", "Keine Zeit")
            st.markdown(f"**Antwort zu Frage {question_number}:**")
            st.markdown(f"> {answer_text}")
            st.markdown(f"*Datum: {date}, Zeit: {time}*")
            st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.write("Keine Texte verfügbar.")

if __name__ == "__main__":
    main()
