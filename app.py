import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt

# App title and instructions
st.title("AI Agent Dashboard")
st.write("Upload a CSV file or connect to a Google Sheet to view, process, and visualize data.")

# File Upload Section
st.subheader("Upload a CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded CSV File:")
    st.write(data.head())
else:
    st.write("No file uploaded yet.")

# Google Sheets Section
st.subheader("Connect to Google Sheets")
sheet_url = st.text_input("Enter Google Sheets URL (must be a public URL)")

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
except FileNotFoundError:
    st.error("credentials.json not found. Make sure it is in the project directory.")

if sheet_url:
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        records = sheet.get_all_records()
        data = pd.DataFrame(records)
        st.write("Preview of Google Sheet Data:")
        st.write(data.head())

        # Allow the user to select a primary column
        primary_column = st.selectbox("Select the primary column", options=data.columns)
        st.write(f"Primary column selected: {primary_column}")

    except Exception as e:
        st.error("Error connecting to Google Sheets. Please check the URL or your credentials.")
        st.write(e)
else:
    st.write("No Google Sheet connected.")

# Data Processing Section
st.subheader("Data Processing Options")
processing_option = st.selectbox("Choose processing type", ["None", "Summarize Data"])

if processing_option == "Summarize Data" and "data" in locals():
    st.write(f"Summary of {primary_column}:")
    st.write(data.describe())

# Data Visualization Section
st.subheader("Data Visualization")
visualization_option = st.selectbox("Choose a chart type", ["None", "Bar Chart", "Pie Chart"])

if visualization_option == "Bar Chart" and "data" in locals():
    st.bar_chart(data[primary_column].value_counts())
elif visualization_option == "Pie Chart" and "data" in locals():
    fig, ax = plt.subplots()
    data[primary_column].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
    st.pyplot(fig)

# Download Processed Data
if "data" in locals():
    st.subheader("Download Processed Data")
    csv = data.to_csv(index=False)
    st.download_button("Download CSV", csv, "processed_data.csv", "text/csv")

