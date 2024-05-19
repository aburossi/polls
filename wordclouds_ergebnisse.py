import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load credentials from Streamlit secrets
credentials_dict = st.secrets["google_credentials"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)
spreadsheet = client.open("WordCloudInputs")  # Replace with your spreadsheet name
worksheet = spreadsheet.sheet1

def get_all_inputs():
    return worksheet.col_values(1)

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud

def main():
    st.title("Word Cloud Generator")

    all_inputs = get_all_inputs()
    combined_text = " ".join(all_inputs)

    if combined_text.strip():
        wordcloud = generate_wordcloud(combined_text)

        st.header("Word Cloud")
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.error("No text available to generate word cloud")

if __name__ == "__main__":
    main()
