import os
import openai
import streamlit as st
import pandas as pd
import gspread
import matplotlib.pyplot as plt
import requests
from google.oauth2 import service_account

# Load credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Load OpenAI and SerpAPI keys from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]
SERPAPI_KEY = st.secrets["serpapi"]["api_key"]

# Function to make a direct API call to SerpAPI
def search_google(query):
    params = {
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Set up Google Sheets client
try:
    client = gspread.authorize(credentials)
except Exception as e:
    st.error("Error loading Google Service Account credentials. Please check your Streamlit secrets.")
    st.stop()

# App title and instructions
st.title("AI Agent Dashboard")
st.write("Upload a CSV file or connect to a Google Sheet to view, process, and retrieve data using AI.")

# File Upload Section
st.subheader("Upload a CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Google Sheets Section
st.subheader("Connect to Google Sheets")
sheet_url = st.text_input("Enter Google Sheets URL (must be a public URL)")

data = None
if uploaded_file:
    # Load CSV file
    data = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded CSV File:")
    st.write(data.head())
elif sheet_url:
    # Load data from Google Sheets
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        records = sheet.get_all_records(expected_headers=True)
        data = pd.DataFrame(records)
        st.write("Preview of Google Sheet Data:")
        st.write(data.head())
    except Exception as e:
        st.error("Error connecting to Google Sheets. Please check the URL or credentials.")

# Processing Options
if data is not None:
    st.subheader("Data Processing Options")

    # Define the primary column
    primary_column = st.selectbox("Select the primary column", options=data.columns)

    # Define the processing option
    process_option = st.selectbox("Choose processing type", ["None", "Summarize Data", "Retrieve Web Data"])

    # Summarize Data
    if process_option == "Summarize Data":
        st.write(f"Summary of {primary_column}:")
        st.write(data[primary_column].describe())

    # Retrieve Web Data (ChatGPT-like Single Query)
    elif process_option == "Retrieve Web Data":
        st.subheader("Web Search Results")
        search_query = st.text_input("Enter search query (use {entity} for entity placeholder)", value="What is AI?")
        if st.button("Start Web Search"):
            try:
                # Allow single query processing
                entity = st.text_input("Enter the specific entity to search:", value="")
                if entity:
                    query = search_query.replace("{entity}", entity)  # Replace placeholder with entity value
                    result = search_google(query)
                    
                    # Extract and display the first relevant result
                    if "organic_results" in result and len(result["organic_results"]) > 0:
                        summary = result["organic_results"][0].get("snippet", "No result found")
                        st.markdown(f"### **Query Result:**\n{summary}")
                    else:
                        st.error("No relevant results found.")
                else:
                    st.error("Please enter a specific entity to search.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Visualization
if data is not None:
    st.subheader("Data Visualization")
    chart_type = st.selectbox("Choose a chart type", ["None", "Bar Chart", "Line Chart", "Pie Chart"])
    if chart_type == "Bar Chart":
        st.bar_chart(data[primary_column].value_counts())
    elif chart_type == "Line Chart":
        st.line_chart(data[primary_column].value_counts())
    elif chart_type == "Pie Chart":
        fig, ax = plt.subplots()
        data[primary_column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

# Footer
st.write("Developed by Shruthi. Powered by OpenAI and SerpAPI.")

