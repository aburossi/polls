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
    worksheet_poll_1 = spreadsheet.worksheet("Umfrage 1")
    worksheet_poll_2 = spreadsheet.worksheet("Umfrage 2")

    st.header("Ranglisten")

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

    fetch_and_display_poll_data(worksheet_poll_1, "Umfrage 1", 'blue')
    fetch_and_display_poll_data(worksheet_poll_2, "Umfrage 2", 'green')

if __name__ == "__main__":
    main()
