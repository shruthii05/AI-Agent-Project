import os
import openai
import streamlit as st
import pandas as pd
import gspread
import matplotlib.pyplot as plt
import requests
from google.oauth2 import service_account

# Set page configuration
st.set_page_config(
    page_title="AI Agent Dashboard",
    page_icon="🤖",
    layout="wide",
)

# Load credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = gspread.authorize(credentials)

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

# Load OpenAI and SerpAPI keys from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]
SERPAPI_KEY = st.secrets["serpapi"]["api_key"]

# Header section
st.markdown(
    """
    <style>
    .main-title {
        font-size: 50px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 22px;
        font-weight: bold;
        color: #333333;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">AI Agent Dashboard 🤖</div>', unsafe_allow_html=True)
st.write(
    "An intelligent dashboard to upload CSV files, connect to Google Sheets, and process data with AI."
)

# Create a two-column layout for file and sheet input
file_col, sheet_col = st.columns(2)

# File Upload Section
with file_col:
    st.markdown('<div class="section-title">Upload a CSV File</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Google Sheets Section
with sheet_col:
    st.markdown('<div class="section-title">Connect to Google Sheets</div>', unsafe_allow_html=True)
    sheet_url = st.text_input("Enter Google Sheets URL (must be a public URL)")

# Data loading
data = None
if uploaded_file:
    # Load CSV file
    data = pd.read_csv(uploaded_file)
    st.success("CSV file successfully loaded!")
    st.write("### Preview of Uploaded CSV File:")
    st.write(data.head())
elif sheet_url:
    # Load data from Google Sheets
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        records = sheet.get_all_records(expected_headers=True)
        data = pd.DataFrame(records)
        st.success("Google Sheet data successfully loaded!")
        st.write("### Preview of Google Sheet Data:")
        st.write(data.head())
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")

# Processing Options
if data is not None:
    st.markdown('<div class="section-title">Data Processing Options</div>', unsafe_allow_html=True)

    # Define the primary column
    primary_column = st.selectbox("Select the primary column", options=data.columns)

    # Define the processing option
    process_option = st.selectbox("Choose processing type", ["None", "Summarize Data", "Retrieve Web Data"])

    # Summarize Data
    if process_option == "Summarize Data":
        st.write(f"### Summary of {primary_column}:")
        st.write(data[primary_column].describe())

    # Retrieve Web Data
    elif process_option == "Retrieve Web Data":
        st.write("### Web Search Results")
        search_query = st.text_input("Enter search query (use {entity} for entity placeholder)", value="What is {entity}")
        if st.button("Start Web Search"):
            results = []  # Initialize results list
            for entity in data[primary_column].unique():  # Process only unique entities
                query = search_query.replace("{entity}", str(entity))  # Replace placeholder with entity value
                try:
                    # Fetch results using search_google function
                    result = search_google(query)

                    # Extract only the first relevant result
                    if "organic_results" in result and len(result["organic_results"]) > 0:
                        # Extract the snippet or title of the first result
                        summary = result["organic_results"][0].get("snippet", "No result found")
                    else:
                        summary = "No relevant results found"

                    # Append to results list
                    results.append({"Entity": entity, "Query": query, "Result": summary})
                except Exception as e:
                    results.append({"Entity": entity, "Query": query, "Result": f"Error: {e}"})

            # Display results in a DataFrame
            results_df = pd.DataFrame(results)
            if not results_df.empty:
                st.write("### Search Results:")
                st.dataframe(results_df, use_container_width=True)

                # Add a download button for the results
                st.download_button(
                    label="Download Results as CSV",
                    data=results_df.to_csv(index=False),
                    file_name="search_results.csv",
                    mime="text/csv",
                )

    # Visualization
    st.markdown('<div class="section-title">Data Visualization</div>', unsafe_allow_html=True)
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
st.markdown(
    """
    <hr>
    <div style="text-align: center; font-size: 16px; color: gray;">
        Developed by <b>Shruthi</b>. Powered by <b>OpenAI</b> and <b>SerpAPI</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

