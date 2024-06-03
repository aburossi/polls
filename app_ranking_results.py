import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import altair as alt

# Constants
SPREADSHEET_NAME = "Rankings"  # Replace with your spreadsheet name
QUESTION_SHEET_NAME = "QandA"  # Sheet name where questions and answers are stored
ANSWER_SHEET_NAMES = ["Umfrage 1", "Umfrage 2"]  # Sheets where the answers are saved

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
        worksheet = spreadsheet.worksheet(worksheet_name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Worksheet '{worksheet_name}' not found in the spreadsheet '{sheet_name}'.")
        return None

# Function to get questions and answers from Google Sheets
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def get_questions():
    client = get_gspread_client()
    worksheet = get_worksheet(client, SPREADSHEET_NAME, QUESTION_SHEET_NAME)
    if worksheet:
        questions = worksheet.get_all_values()
        # Transpose the data to get questions in columns
        questions = list(zip(*questions))
        return questions
    return []

# Function to fetch and display poll data
def fetch_and_display_poll_data(worksheet, poll_name, color):
    try:
        # Fetch data from the worksheet
        all_rankings = worksheet.get_all_records()
        if all_rankings:
            results_df = pd.DataFrame(all_rankings, columns=["Rank", "Choice"])
            results_df["Rank"] = pd.to_numeric(results_df["Rank"])
            average_ranks = results_df.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks.columns = ["Choice", "Average Rank"]
            average_ranks = average_ranks.sort_values(by="Average Rank", ascending=True)

            # Display the results as a bar chart
            chart = alt.Chart(average_ranks).mark_bar(color=color).encode(
                x=alt.X("Average Rank:Q", axis=alt.Axis(title="Durchschnittliche Bewertung")),
                y=alt.Y("Choice:N", sort=alt.SortField(field="Average Rank", order="ascending"), axis=alt.Axis(title="Auswahl"))
            ).properties(
                title=f"Durchschnittliche Bewertung der Auswahlmöglichkeiten - {poll_name}"
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.write(f"No data available for {poll_name}.")
    except Exception as e:
        st.error(f"An error occurred while processing {poll_name}: {e}")

def main():
    # Initialize Google Sheets client
    client = get_gspread_client()

    st.header("Ranglisten")

    # Load questions and answers from Google Sheets
    questions = get_questions()

    # Display results for each poll
    for i, worksheet_name in enumerate(ANSWER_SHEET_NAMES):
        worksheet = get_worksheet(client, SPREADSHEET_NAME, worksheet_name)
        if worksheet and i < len(questions):
            question = questions[i][0]
            fetch_and_display_poll_data(worksheet, question, 'blue' if i % 2 == 0 else 'green')

    # Button to clear data from both worksheets
    if st.button("Delete Data from Google Sheets"):
        try:
            for worksheet_name in ANSWER_SHEET_NAMES:
                worksheet = get_worksheet(client, SPREADSHEET_NAME, worksheet_name)
                if worksheet:
                    worksheet.clear()
            st.success("Data successfully deleted from both worksheets.")
        except Exception as e:
            st.error(f"An error occurred while deleting data: {e}")

if __name__ == "__main__":
    main()
