kimport os
import openai
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import matplotlib.pyplot as plt
import requests

# Load credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = gspread.authorize(credentials)

# Set page configuration for an attractive UI
st.set_page_config(
    page_title="AI Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        color: white;
        background-color: #4caf50;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 8px;
    }
    .stDownloadButton>button {
        background-color: #2196f3;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
    }
    h2, h3, h4 {
        color: #333;
        font-family: Arial, sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to make a direct API call to SerpAPI
def search_google(query):
    """Fetches web results from SerpAPI."""
    params = {
        "q": query,
        "hl": "en",
        "api_key": st.secrets["serpapi"]["api_key"],
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Load OpenAI and SerpAPI keys from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# App title
st.title("🤖 AI Agent Dashboard")
st.write(
    """
    Welcome to the AI Agent Dashboard! You can upload a CSV file or connect to a Google Sheet to analyze data, 
    retrieve web results, and visualize insights.
    """
)

# File Upload Section
st.subheader("📂 Upload a CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Google Sheets Section
st.subheader("🔗 Connect to Google Sheets")
sheet_url = st.text_input("Enter Google Sheets URL (must be a public URL)")

data = None
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("### 📋 Preview of Uploaded CSV File")
    st.dataframe(data, use_container_width=True)
elif sheet_url:
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        records = sheet.get_all_records(expected_headers=True)
        data = pd.DataFrame(records)
        st.write("### 📋 Preview of Google Sheet Data")
        st.dataframe(data, use_container_width=True)
    except Exception as e:
        st.error("Error connecting to Google Sheets. Please check the URL or credentials.")

# Processing Options
if data is not None:
    st.subheader("⚙️ Data Processing Options")

    # Define the primary column
    primary_column = st.selectbox("Select the primary column", options=data.columns)

    # Define the processing option
    process_option = st.selectbox("Choose processing type", ["None", "Summarize Data", "Retrieve Web Data"])

    # Summarize Data
    if process_option == "Summarize Data":
        st.write(f"### 🔍 Summary of '{primary_column}'")
        st.write(data[primary_column].describe())

    # Retrieve Web Data
    elif process_option == "Retrieve Web Data":
        st.subheader("🌐 Web Search Results")
        search_query = st.text_input(
            "Enter your search query (e.g., 'What is {entity}?' or 'Explain {entity}')",
            value="What is {entity}",
        )

        if "{entity}" in search_query:
            default_entity = data[primary_column].unique()[0] if not data[primary_column].empty else ""
            entity = st.text_input("Enter the specific entity to search:", value=default_entity)
            query = search_query.replace("{entity}", entity)
        else:
            query = search_query

        if st.button("Start Web Search"):
            if query:
                result = search_google(query)
                if "organic_results" in result and len(result["organic_results"]) > 0:
                    summary = result["organic_results"][0].get("snippet", "No result found")
                    st.markdown(f"### **Query Result:**\n{summary}")
                else:
                    st.error("No relevant results found.")
            else:
                st.error("Please enter a valid search query.")

    # Visualization
    st.subheader("📊 Data Visualization")
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
st.write(
    """
    ---
    Developed by Shruthi. Powered by OpenAI, SerpAPI, and Google Cloud.
    """
)

