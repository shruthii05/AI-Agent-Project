import os
import openai
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import requests

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

# Load OpenAI and SerpAPI keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Check if the keys are loaded successfully
if not openai.api_key:
    st.error("OpenAI API key is missing. Please set it as an environment variable.")
if not SERPAPI_KEY:
    st.error("SerpAPI key is missing. Please set it as an environment variable.")

# App title and instructions
st.title("AI Agent Dashboard")
st.write("Upload a CSV file or connect to a Google Sheet to view, process, and retrieve data using AI.")

# File Upload Section
st.subheader("Upload a CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

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
    
    # Ensure 'process_option' is now available and usable
    # Summarize Data
    if process_option == "Summarize Data":
        st.write(f"Summary of {primary_column}:")
        st.write(data[primary_column].describe())
    
    # Retrieve Web Data
    elif process_option == "Retrieve Web Data":
        search_query = st.text_input("Enter search query (use {entity} for entity placeholder)", value="What is {entity}")
        if st.button("Start Web Search"):
            results = []  # Initialize results list
            for entity in data[primary_column].unique():  # Process only unique entities
                query = search_query.replace("{entity}", str(entity))  # Replace placeholder with entity value
                try:
                    # Fetch results using search_google function
                    result = search_google(query)
                    if "organic_results" in result and len(result["organic_results"]) > 0:
                        # Extract the first snippet from results
                        summary = result["organic_results"][0].get("snippet", "No result found")
                    else:
                        summary = "No relevant results found"

                    # Append to results list
                    results.append({"Entity": entity, "Query": query, "Result": summary})
                except Exception as e:
                    results.append({"Entity": entity, "Query": query, "Result": f"Error: {e}"})
            
            # Display results in a DataFrame
            st.write("Search Results:")
            results_df = pd.DataFrame(results)
            st.write(results_df)
            
            # Add download option
            st.download_button("Download Results", results_df.to_csv(index=False), file_name="search_results.csv")

      
 
    # Visualization
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


