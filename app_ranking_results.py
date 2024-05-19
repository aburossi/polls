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
    worksheet = spreadsheet.sheet1

    st.header("Previous Rankings")
    try:
        all_rankings = worksheet.get_all_records()
        if all_rankings:
            results_df = pd.DataFrame(all_rankings, columns=["Rank", "Choice"])

            # Convert "Rank" to numeric
            results_df["Rank"] = pd.to_numeric(results_df["Rank"])

            # Calculate average rank for each choice
            average_ranks = results_df.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks.columns = ["Choice", "Average Rank"]
            average_ranks = average_ranks.sort_values(by="Average Rank")

            # Display the results as a bar chart
            chart = alt.Chart(average_ranks).mark_bar().encode(
                x=alt.X("Average Rank:Q", axis=alt.Axis(title="Average Rank")),
                y=alt.Y("Choice:N", sort='-x', axis=alt.Axis(title="Choice"))
            ).properties(
                title="Average Ranking of Choices"
            )

            st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
