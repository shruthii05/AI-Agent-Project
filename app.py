import os
import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Set page configuration
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

# Header Section
st.markdown(
    """
    <style>
        .main-header { text-align: center; color: #0057D9; }
        .main-header h1 { font-size: 3.5em; margin-bottom: 5px; }
        .main-header p { font-size: 1.2em; color: #555; }
        .section-header { color: #007bff; margin-bottom: 20px; }
        .card { background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
        .success-box { background-color: #e6f7e6; padding: 15px; border-radius: 10px; border: 1px solid #34a853; color: #34a853; font-weight: bold; }
    </style>
    <div class="main-header">
        <h1>🚀 QueryScope AI</h1>
        <p>Empowering data search and visualization with <span style="color: #FF4500;">AI</span></p>
    </div>
    <hr style="border: 1px solid #EEE; margin: 20px 0;">
    """,
    unsafe_allow_html=True,
)

# File Upload Section
st.markdown("<h2 class='section-header'>📂 Upload Your Data</h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV file for processing", type=["csv"])

data = None
if uploaded_file:
    try:
        data = pd.read_csv(uploaded_file)
        st.markdown("<div class='success-box'>✅ CSV file uploaded successfully!</div>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #34a853;'>Preview of Uploaded CSV File:</h3>", unsafe_allow_html=True)
        st.dataframe(data.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Error reading the uploaded file: {e}")

if data is not None:
    st.markdown("<h2 class='section-header'>⚙️ Data Processing Options</h2>", unsafe_allow_html=True)
    process_option = st.selectbox("Choose processing type:", ["None", "Summarize Data", "Retrieve Web Data"])
    
    if process_option == "Summarize Data":
        primary_column = st.selectbox("Select the primary column to summarize:", options=data.columns)
        st.markdown(f"<h3>Summary of {primary_column}:</h3>", unsafe_allow_html=True)
        st.write(data[primary_column].describe())

    elif process_option == "Retrieve Web Data":
        primary_column = st.selectbox("Select the primary column for web data retrieval:", options=data.columns)
        search_query_template = st.text_input("Enter search query (use {entity} for entity placeholder):", value="What is {entity}?")
        user_input = st.text_input("Ask about an entity (e.g., 'Chile'):", value="")

        if st.button("Start Web Search"):
            st.markdown("## 🔍 Web Search Results")
            results = {}

            if user_input:
                query = search_query_template.replace("{entity}", user_input)
                try:
                    result = search_google(query)
                    if "organic_results" in result and len(result["organic_results"]) > 0:
                        summary = result["organic_results"][0].get("snippet", "No result found")
                        link = result["organic_results"][0].get("link", "")
                        summary = f"{summary}\n\n[Read more here]({link})"
                    else:
                        summary = "No relevant results found"
                    results[user_input] = summary
                except Exception as e:
                    results[user_input] = f"Error: {e}"

                response = results.get(user_input, "No relevant results found for the given query.")
                st.markdown(f"**User:** {user_input}\n\n**AI:** {response}", unsafe_allow_html=True)

            else:
                st.warning("Please enter an entity to search.")

            # Download Results as CSV
            if results:
                results_df = pd.DataFrame(list(results.items()), columns=["Entity", "Response"])
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=results_df.to_csv(index=False),
                    file_name="search_results.csv",
                    mime="text/csv",
                )

else:
    st.warning("Please upload a CSV file to proceed.")
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
