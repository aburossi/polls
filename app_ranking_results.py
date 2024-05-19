import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import altair as alt

def main():
    # Load credentials from Streamlit secrets
    credentials_dict = st.secrets["google_credentials"]

    # Initialize Google Sheets client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("Rankings")  # Replace with your spreadsheet name
    worksheet_poll_1 = spreadsheet.worksheet("Poll 1")
    worksheet_poll_2 = spreadsheet.worksheet("Poll 2")

    st.header("Previous Rankings")
    try:
        # Fetch data from Poll 1
        all_rankings_poll_1 = worksheet_poll_1.get_all_records()
        if all_rankings_poll_1:
            results_df_poll_1 = pd.DataFrame(all_rankings_poll_1, columns=["Rank", "Choice"])
            results_df_poll_1["Rank"] = pd.to_numeric(results_df_poll_1["Rank"])
            average_ranks_poll_1 = results_df_poll_1.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks_poll_1.columns = ["Choice", "Average Rank"]
            average_ranks_poll_1["Poll"] = "Poll 1"

        # Fetch data from Poll 2
        all_rankings_poll_2 = worksheet_poll_2.get_all_records()
        if all_rankings_poll_2:
            results_df_poll_2 = pd.DataFrame(all_rankings_poll_2, columns=["Rank", "Choice"])
            results_df_poll_2["Rank"] = pd.to_numeric(results_df_poll_2["Rank"])
            average_ranks_poll_2 = results_df_poll_2.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks_poll_2.columns = ["Choice", "Average Rank"]
            average_ranks_poll_2["Poll"] = "Poll 2"

        # Combine data for both polls
        combined_df = pd.concat([average_ranks_poll_1, average_ranks_poll_2])

        # Display the results as a bar chart with different colors for each poll
        chart = alt.Chart(combined_df).mark_bar().encode(
            x=alt.X("Average Rank:Q", axis=alt.Axis(title="Average Rank")),
            y=alt.Y("Choice:N", sort='-x', axis=alt.Axis(title="Choice")),
            color=alt.Color("Poll:N", legend=alt.Legend(title="Poll"))
        ).properties(
            title="Average Ranking of Choices"
        )

        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
