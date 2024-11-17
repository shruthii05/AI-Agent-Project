import os
import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

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

# App title and header
st.markdown(
    """
    <div style="text-align: center; margin-top: -30px; margin-bottom: 20px;">
        <h1 style="font-size: 2.5em; color: #2C6E91;">🚀 AI Agent Dashboard</h1>
        <p style="font-size: 1.2em; color: #555;">Simplifying Data Search and Analysis with AI</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# File Upload Section
st.subheader("📂 Upload Your Data")
uploaded_file = st.file_uploader("Upload a CSV file for processing.", type="csv")

data = None
if uploaded_file:
    # Load CSV file
    data = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded CSV File:")
    st.write(data.head())

# Processing Options
if data is not None:
    st.subheader("⚙️ Data Processing Options")
    primary_column = st.selectbox("Select the primary column to process", options=data.columns)
    process_option = st.selectbox("Choose processing type", ["None", "Summarize Data", "Retrieve Web Data"])

    if process_option == "Summarize Data":
        st.write(f"Summary of {primary_column}:")
        st.write(data[primary_column].describe())
    elif process_option == "Retrieve Web Data":
        search_query = st.text_input("Enter search query (use {entity} for entity placeholder)", value="What is {entity}")
        if st.button("Start Web Search"):
            st.subheader("🔍 Web Search Results")
            unique_entities = data[primary_column].drop_duplicates().tolist()  # Ensure unique queries only
            results = []

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

                results.append({"Query": query, "Response": summary})

            # Display results in ChatGPT-style format
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

# Data Visualization
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
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; font-size: 0.9em; color: #888;">
        Developed by Shruthi. Powered by <span style="color: #007bff;">OpenAI</span>, 
        <span style="color: #FF4500;">SerpAPI</span>.
    </div>
    """,
    unsafe_allow_html=True,
)

