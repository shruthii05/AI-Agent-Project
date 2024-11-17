import os
import openai
import streamlit as st
import pandas as pd
import gspread
import matplotlib.pyplot as plt
from google.oauth2 import service_account

# Load credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

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

try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = gspread.authorize(creds)
except Exception as e:
    st.error("Error loading Google Service Account credentials. Please check your Streamlit secrets.")
    st.stop()

# Header Section with Styling
st.markdown(
    """
    <style>
        .header {
            text-align: center;
            padding: 20px;
            background-color: #f3f4f6;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2d6a4f;
            font-size: 2.5em;
        }
        .header h4 {
            color: #40916c;
            font-weight: normal;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #6c757d;
        }
    </style>
    <div class="header">
        <h1>🌟 AI Agent Dashboard</h1>
        <h4>Simplifying Data Search and Analysis with AI</h4>
    </div>
    """,
    unsafe_allow_html=True,
)

# File Upload Section
st.subheader("📁 Upload Your Data")
st.markdown("Upload a CSV file or connect to a Google Sheet for processing.")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

sheet_url = st.text_input("Enter Google Sheets URL (must be public)")

data = None
if uploaded_file:
    # Load CSV file
    data = pd.read_csv(uploaded_file)
    st.write("📄 **Preview of Uploaded CSV File:**")
    st.write(data.head())
elif sheet_url:
    # Load data from Google Sheets
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        records = sheet.get_all_records(expected_headers=True)
        data = pd.DataFrame(records)
        st.write("📄 **Preview of Google Sheet Data:**")
        st.write(data.head())
    except Exception as e:
        st.error("Error connecting to Google Sheets. Please check the URL or credentials.")

# Data Processing Section
if data is not None:
    st.markdown("---")
    st.subheader("⚙️ Data Processing Options")
    primary_column = st.selectbox("Select the primary column to process", options=data.columns)
    process_option = st.selectbox("Choose processing type", ["None", "Summarize Data", "Retrieve Web Data"])

    if process_option == "Summarize Data":
        st.write(f"📊 **Summary of {primary_column}:**")
        st.write(data[primary_column].describe())
    elif process_option == "Retrieve Web Data":
        search_query = st.text_input("Enter search query (use {entity} for entity placeholder)", value="What is {entity}")
        if st.button("Start Web Search"):
            results = []
            for entity in data[primary_column].unique():
                query = search_query.replace("{entity}", str(entity))
                try:
                    result = search_google(query)
                    summary = result.get("organic_results", [{}])[0].get("snippet", "No result found")
                    results.append({"Entity": entity, "Query": query, "Result": summary})
                except Exception as e:
                    results.append({"Entity": entity, "Query": query, "Result": f"Error: {e}"})

            results_df = pd.DataFrame(results)
            st.write("🔍 **Search Results:**")
            st.dataframe(results_df, use_container_width=True)
            st.download_button(
                label="📥 Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name="search_results.csv",
                mime="text/csv",
            )

# Data Visualization Section
if data is not None:
    st.markdown("---")
    st.subheader("📊 Data Visualization")
    visualization_column = st.selectbox("Select the column to visualize", options=data.columns)
    chart_type = st.selectbox("Choose a chart type", ["None", "Bar Chart", "Line Chart", "Pie Chart"])

    if chart_type == "Bar Chart":
        st.bar_chart(data[visualization_column].value_counts())
    elif chart_type == "Line Chart":
        st.line_chart(data[visualization_column].value_counts())
    elif chart_type == "Pie Chart":
        fig, ax = plt.subplots()
        data[visualization_column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

# Footer Section
st.markdown(
    """
    <div class="footer">
        Developed by <b>Shruthi</b> | Powered by <a href="https://openai.com" style="text-decoration:none;">OpenAI</a>, <a href="https://serpapi.com" style="text-decoration:none;">SerpAPI</a>, and <a href="https://cloud.google.com/" style="text-decoration:none;">Google Cloud</a> 🌐
    </div>
    """,
    unsafe_allow_html=True,
)


