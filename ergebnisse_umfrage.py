import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt

# Constants
SPREADSHEET_NAME = "Umfrage"  # The name of the spreadsheet
ANSWER_SHEET_NAME = "sheet1"  # The sheet where the answers are saved

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
    try:
        spreadsheet = client.open(sheet_name)
        return spreadsheet.worksheet(worksheet_name)
    except gspread.SpreadsheetNotFound:
        st.error(f"Spreadsheet '{sheet_name}' not found. Please check the name and try again.")
        return None
    except gspread.WorksheetNotFound:
        st.error(f"Worksheet '{worksheet_name}' not found in the spreadsheet '{sheet_name}'.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to load responses from Google Sheets
def load_responses():
    client = get_gspread_client()
    worksheet = get_worksheet(client, SPREADSHEET_NAME, ANSWER_SHEET_NAME)
    if worksheet:
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

# Function to plot pie chart
def plot_pie_chart(responses, question):
    response_counts = responses.value_counts()
    labels = response_counts.index
    sizes = response_counts.values

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

# Main function
def main():
    st.title("Survey Results")

    df = load_responses()
    if not df.empty:
        questions = df['Question'].unique()
        for question in questions:
            st.write(f"**{question}**")
            responses = df[df['Question'] == question]['Answer']
            plot_pie_chart(responses, question)
    else:
        st.write("No responses found.")

if __name__ == "__main__":
    main()
