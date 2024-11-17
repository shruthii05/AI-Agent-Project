import os
import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Set page layout to wide and define page title
st.set_page_config(page_title="QueryScope AI", layout="wide")

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

# App title and header with refined styling
st.markdown(
    """
    <style>
        .main-header {
            text-align: center;
            color: #0057D9;
        }
        .main-header h1 {
            font-size: 3.5em;
            margin-bottom: 5px;
        }
        .main-header p {
            font-size: 1.2em;
            color: #555;
        }
        .section-header {
            color: #007bff;
            margin-bottom: 20px;
        }
        .card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .success-box {
            background-color: #e6f7e6;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #34a853;
            color: #34a853;
            font-weight: bold;
        }
    </style>
    <div class="main-header">
        <h1>🚀 QueryScope AI</h1>
        <p>Empowering data search and visualization with <span style="color: #FF4500;">AI</span></p>
    </div>
    <hr style="border: 1px solid #EEE; margin: 20px 0;">
    """,
    unsafe_allow_html=True,
)

# File Upload Section with success feedback
st.markdown(
    """
    <h2 class="section-header">📂 Upload Your Data</h2>
    <p>Upload a CSV file for processing. The uploaded data will be used for search and visualization.</p>
    """,
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader(
    "Drag and drop your CSV file here or click to browse.", type="csv"
)

data = None
if uploaded_file:
    # Load CSV file
    data = pd.read_csv(uploaded_file)
    st.markdown(
        """
        <div class="success-box">✅ CSV file uploaded successfully!</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <h3 style="color: #000000; margin-top: 20px;">Preview of Uploaded CSV File:</h3>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(data.head(), use_container_width=True)

# Processing Options
if data is not None:
    st.markdown(
        """
        <h2 class="section-header">⚙️ Data Processing Options</h2>
        """,
        unsafe_allow_html=True,
    )
# Dropdown to select the primary column to process
primary_column = st.selectbox("Select the primary column to process:", options=data.columns)

# Dropdown to select the processing type
process_option = st.selectbox("Choose processing type:", ["None", "Summarize Data", "Retrieve Web Data"])

# Conditional for summarizing data
if process_option == "Summarize Data":
    st.markdown(f"<h3>Summary of {primary_column}:</h3>", unsafe_allow_html=True)
    st.write(data[primary_column].describe())

# Conditional for retrieving web data
elif process_option == "Retrieve Web Data":
    search_query = st.text_input("Enter search query (use {entity} for entity placeholder)", value="What is {entity}")
    if st.button("Start Web Search"):
        st.subheader("🔍 Web Search Results")
        unique_entities = data[primary_column].drop_duplicates().tolist()  # Ensure unique queries only
        results = []
        
        # Loop through unique entities and perform a search
        for entity in unique_entities:
            query = search_query.replace("{entity}", str(entity))
            try:
                result = search_google(query)
                if "organic_results" in result and len(result["organic_results"]) > 0:
                    summary = result["organic_results"][0].get("snippet", "No result found")
                else:
                    summary = "No relevant results found"
            except Exception as e:
                summary = f"Error: {e}"
            
            # Append only unique query-response pairs
            if not any(res["Query"] == query for res in results):
                results.append({"Query": query, "Response": summary})
        
        # Display results
        for result in results:
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                    <p><strong>Query:</strong> {result["Query"]}</p>
                    <p><strong>Response:</strong> {result["Response"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        # Add a download button for results
        if results:
            results_df = pd.DataFrame(results)
            st.download_button(
                label="Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name="web_search_results.csv",
                mime="text/csv",
            )

        # Display 
results in a ChatGPT-style format
        if results:
            for result in results:
                st.markdown(
                    f"""
                    <div style="background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                        <p><strong>Query:</strong> {result["Query"]}</p>
                        <p><strong>Response:</strong> {result["Response"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
# Data Visualization Section
    st.markdown(
        """
        <h2 class="section-header">📊 Data Visualization</h2>
        """,
        unsafe_allow_html=True,
    )
    chart_type = st.selectbox("Choose a chart type:", ["None", "Bar Chart", "Line Chart", "Pie Chart"])
    if chart_type == "Bar Chart":
        st.bar_chart(data[primary_column].value_counts())
    elif chart_type == "Line Chart":
        st.line_chart(data[primary_column].value_counts())
    elif chart_type == "Pie Chart":
        fig, ax = plt.subplots()
        data[primary_column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

# Footer with a professional look
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; font-size: 0.9em; color: #888;">
        Developed by Shruthi. Powered by <span style="color: #007bff;">OpenAI</span> 
        and <span style="color: #FF4500;">SerpAPI</span>.
    </div>
    """,
    unsafe_allow_html=True,
)

