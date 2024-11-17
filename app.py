import os
import openai
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import matplotlib.pyplot as plt
import requests

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
        "api_key": st.secrets["serpapi"]["api_key"],
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Load OpenAI and SerpAPI keys
openai.api_key = st.secrets["openai"]["api_key"]

# Add header image
st.markdown(
    """
    <style>
    .main-title {
        font-size: 3em;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .sub-title {
        font-size: 1.5em;
        text-align: center;
        color: #555;
        margin-bottom: 30px;
    }
    .header-image {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 50%;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

header_image_url = "https://via.placeholder.com/800x200.png?text=AI+Agent+Dashboard"  # Replace with a relevant image URL
st.markdown(f'<img src="{header_image_url}" class="header-image">', unsafe_allow_html=True)
st.markdown('<div class="main-title">AI Agent Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Simplifying Data Search and Analysis with AI</div>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio(
    "Go to",
    ["📂 Upload Data", "🔍 Web Search Results", "📊 Data Visualization"],
    index=0,
)

# File Upload Section
if options == "📂 Upload Data":
    st.markdown("### 📂 Upload Your Data")
    st.write("Upload a CSV file or connect to a Google Sheet for processing.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    sheet_url = st.text_input("Enter Google Sheets URL (must be public)")

    data = None
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.write("### 📋 Preview of Uploaded CSV")
        st.dataframe(data, use_container_width=True)
    elif sheet_url:
        try:
            sheet = client.open_by_url(sheet_url).sheet1
            records = sheet.get_all_records(expected_headers=True)
            data = pd.DataFrame(records)
            st.success("✅ Google Sheet connected successfully!")
            st.write("### 📋 Preview of Google Sheet Data")
            st.dataframe(data, use_container_width=True)
        except Exception as e:
            st.error("❌ Error connecting to Google Sheets. Please check the URL or credentials.")

    # Store data in session state
    if data is not None:
        st.session_state["data"] = data

# Web Search Results Section
elif options == "🔍 Web Search Results":
    st.markdown("### 🔍 Search Web Data")
    if "data" in st.session_state:
        data = st.session_state["data"]
        primary_column = st.selectbox(
            "Select the primary column for entities", options=data.columns
        )
        search_query = st.text_input(
            "Enter your search query (e.g., 'What is {entity}?')",
            value="What is {entity}",
        )
        if st.button("Start Search"):
            results = []
            for entity in data[primary_column].unique():
                query = search_query.replace("{entity}", str(entity))
                try:
                    result = search_google(query)
                    if "organic_results" in result and len(result["organic_results"]) > 0:
                        summary = result["organic_results"][0].get(
                            "snippet", "No result found"
                        )
                    else:
                        summary = "No relevant results found"
                    results.append(
                        {"Entity": entity, "Query": query, "Result": summary}
                    )
                except Exception as e:
                    results.append(
                        {"Entity": entity, "Query": query, "Result": f"Error: {e}"}
                    )

            results_df = pd.DataFrame(results)
            st.success("✅ Search completed!")
            st.write("### 🌐 Search Results")
            st.dataframe(results_df, use_container_width=True)

            # Add a download button
            st.download_button(
                label="📥 Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name="search_results.csv",
                mime="text/csv",
            )
    else:
        st.warning("⚠️ Please upload data first in the '📂 Upload Data' section.")

# Data Visualization Section
elif options == "📊 Data Visualization":
    st.markdown("### 📊 Data Visualization")
    if "data" in st.session_state:
        data = st.session_state["data"]
        primary_column = st.selectbox(
            "Select the column to visualize", options=data.columns
        )
        chart_type = st.selectbox(
            "Choose a chart type", ["None", "Bar Chart", "Line Chart", "Pie Chart"]
        )
        if chart_type == "Bar Chart":
            st.bar_chart(data[primary_column].value_counts())
        elif chart_type == "Line Chart":
            st.line_chart(data[primary_column].value_counts())
        elif chart_type == "Pie Chart":
            fig, ax = plt.subplots()
            data[primary_column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
            st.pyplot(fig)
    else:
        st.warning("⚠️ Please upload data first in the '📂 Upload Data' section.")

# Footer
st.markdown(
    """
    ---
    <div style="text-align: center;">
        <strong>Developed by Shruthi</strong><br>
        Powered by <span style="color: #FF6F61;">OpenAI</span>, 
        <span style="color: #4285F4;">SerpAPI</span>, 
        and <span style="color: #34A853;">Google Cloud</span>.
    </div>
    """,
    unsafe_allow_html=True,
)

