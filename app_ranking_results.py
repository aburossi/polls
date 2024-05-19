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
    worksheet_poll_3 = spreadsheet.worksheet("Poll 3")

    st.header("Previous Rankings")
    try:
        # Fetch data from Poll 1
        all_rankings_poll_1 = worksheet_poll_1.get_all_records()
        if all_rankings_poll_1:
            results_df_poll_1 = pd.DataFrame(all_rankings_poll_1, columns=["Rank", "Choice"])
            results_df_poll_1["Rank"] = pd.to_numeric(results_df_poll_1["Rank"])
            average_ranks_poll_1 = results_df_poll_1.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks_poll_1.columns = ["Choice", "Average Rank"]
            average_ranks_poll_1 = average_ranks_poll_1.sort_values(by="Average Rank", ascending=True)

            # Display the results as a bar chart for Poll 1
            chart_poll_1 = alt.Chart(average_ranks_poll_1).mark_bar(color='blue').encode(
                x=alt.X("Average Rank:Q", axis=alt.Axis(title="Average Rank")),
                y=alt.Y("Choice:N", sort=alt.SortField(field="Average Rank", order="ascending"), axis=alt.Axis(title="Choice"))
            ).properties(
                title="Average Ranking of Choices - Poll 1"
            )

            st.altair_chart(chart_poll_1, use_container_width=True)

        # Fetch data from Poll 2
        all_rankings_poll_2 = worksheet_poll_2.get_all_records()
        if all_rankings_poll_2:
            results_df_poll_2 = pd.DataFrame(all_rankings_poll_2, columns=["Rank", "Choice"])
            results_df_poll_2["Rank"] = pd.to_numeric(results_df_poll_2["Rank"])
            average_ranks_poll_2 = results_df_poll_2.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks_poll_2.columns = ["Choice", "Average Rank"]
            average_ranks_poll_2 = average_ranks_poll_2.sort_values(by="Average Rank", ascending=True)

            # Display the results as a bar chart for Poll 2
            chart_poll_2 = alt.Chart(average_ranks_poll_2).mark_bar(color='green').encode(
                x=alt.X("Average Rank:Q", axis=alt.Axis(title="Average Rank")),
                y=alt.Y("Choice:N", sort=alt.SortField(field="Average Rank", order="ascending"), axis=alt.Axis(title="Choice"))
            ).properties(
                title="Average Ranking of Choices - Poll 2"
            )

            st.altair_chart(chart_poll_2, use_container_width=True)

        # Fetch data from Poll 3
        all_rankings_poll_3 = worksheet_poll_3.get_all_records()
        if all_rankings_poll_3:
            results_df_poll_3 = pd.DataFrame(all_rankings_poll_3, columns=["Rank", "Choice"])
            results_df_poll_3["Rank"] = pd.to_numeric(results_df_poll_3["Rank"])
            average_ranks_poll_3 = results_df_poll_3.groupby("Choice")["Rank"].mean().reset_index()
            average_ranks_poll_3.columns = ["Choice", "Average Rank"]
            average_ranks_poll_3 = average_ranks_poll_3.sort_values(by="Average Rank", ascending=True)

            # Display the results as a bar chart for Poll 3
            chart_poll_3 = alt.Chart(average_ranks_poll_3).mark_bar(color='red').encode(
                x=alt.X("Average Rank:Q", axis=alt.Axis(title="Average Rank")),
                y=alt.Y("Choice:N", sort=alt.SortField(field="Average Rank", order="ascending"), axis=alt.Axis(title="Choice"))
            ).properties(
                title="Average Ranking of Choices - Poll 3"
            )

            st.altair_chart(chart_poll_3, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
