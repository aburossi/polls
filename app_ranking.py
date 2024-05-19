import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from streamlit_cookies_manager import EncryptedCookieManager
import pandas as pd
import altair as alt

def main():
    # Define the choices
    choices = ["Option A", "Option B", "Option C", "Option D"]

    # Load credentials from Streamlit secrets
    credentials_dict = st.secrets["google_credentials"]

    # Initialize Google Sheets client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("Rankings")  # Replace with your spreadsheet name
    worksheet = spreadsheet.sheet1

    # Initialize cookies manager
    cookies = EncryptedCookieManager(prefix="rank_", password=credentials_dict["cookie_password"])

    if not cookies.ready():
        st.stop()

    # Check if the user has submitted in the last 24 hours
    last_submission = cookies.get("last_submission")
    if last_submission:
        last_submission_time = datetime.datetime.fromisoformat(last_submission)
        if (datetime.datetime.now() - last_submission_time).days < 1:
            st.session_state.has_submitted = True
    else:
        st.session_state.has_submitted = False

    st.title("Rank the Choices from Most Important to Least Important")

    if st.session_state.has_submitted:
        st.write("You have already submitted your rankings today. Thank you!")
    else:
        # Create containers to hold the rankings
        rankings = {}

        # Loop through the choices to create ranking selectors
        for i in range(1, len(choices) + 1):
            available_choices = [choice for choice in choices if choice not in rankings.values()]
            rankings[i] = st.selectbox(f"Rank {i}", available_choices, key=i)

        # Function to add rankings to the Google Sheet
        def add_rankings_to_sheet(rankings):
            rows = [[rank, choice] for rank, choice in rankings.items()]
            worksheet.append_rows(rows)

        # Display the rankings and submit button
        if st.button("Submit Rankings"):
            add_rankings_to_sheet(rankings)
            cookies["last_submission"] = datetime.datetime.now().isoformat()
            cookies.save()
            st.session_state.has_submitted = True
            st.success("Rankings submitted successfully!")

    # Display the results from previous sessions
    st.header("Previous Rankings")
    try:
        all_rankings = worksheet.get_all_records()
        if all_rankings:
            results_df = pd.DataFrame(all_rankings, columns=["Rank", "Choice"])

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
