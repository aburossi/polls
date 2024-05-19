# results_app.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define static questions and answers
questions = [
    "Frage 1",
    "Frage 2",
    "Frage 3"
]

# Initialize Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)
spreadsheet = client.open("Umfrage")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

# Function to get all responses from the Google Sheet
def get_all_responses():
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

# Display results
try:
    all_responses = get_all_responses()
    if not all_responses.empty:
        st.header("Poll Results")
        results_df = pd.DataFrame(all_responses)
        
        # Ensure column headers are present
        if 'Question' not in results_df.columns or 'Answer' not in results_df.columns:
            st.error("Data format error: Ensure the first row of your Google Sheet contains 'Question' and 'Answer' headers.")
        else:
            for question in questions:
                st.write(f"**{question}**")
                response_data = results_df[results_df['Question'] == question]['Answer'].value_counts()
                st.bar_chart(response_data)
except Exception as e:
    st.error(f"An error occurred: {e}")

# Debugging: Print all responses
st.write("All responses from the sheet:")
st.write(all_responses)
