import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt

# Define static questions and answers
questions = [
    "1. Frage",
    "2. Frage",
    "3. Frage"
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

# Function to plot the bar chart with custom colors
def plot_bar_chart(data, title, color):
    fig, ax = plt.subplots()
    data.plot(kind='bar', ax=ax, color=color)
    ax.set_title(title)
    ax.set_ylabel('Count')
    st.pyplot(fig)

# Define colors for each question
colors = ['#FF6347', '#4682B4', '#32CD32']  # Different colors for each question

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
            for idx, question in enumerate(questions):
                st.write(f"**{question}**")
                response_data = results_df[results_df['Question'] == question]['Answer'].value_counts()
                plot_bar_chart(response_data, question, colors[idx])
    else:
        st.write("No responses found.")
except Exception as e:
    st.error(f"An error occurred: {e}")

# Button to clear data from the worksheet
if st.button("Delete Data from Google Sheet"):
    try:
        worksheet.clear()
        st.success("Data successfully deleted from the worksheet.")
    except Exception as e:
        st.error(f"An error occurred while deleting data: {e}")
