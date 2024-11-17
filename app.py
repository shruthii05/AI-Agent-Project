kimport os
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

# App title and header with a better design
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 3em; color: #2E86C1; font-weight: bold;">🚀 AI Agent Dashboard</h1>
        <p style="font-size: 1.2em; color: #555;">Empowering data search and visualization with AI</p>
        <hr style="border: none; height: 2px; background-color: #2E86C1; margin-top: 10px; width: 80%;">
    </div>
    """,
    unsafe_allow_html=True,
)

# File Upload Section with emoji
st.subheader("📂 Upload Your Data")
st.markdown(
    """
    <p style="color: #444;">You can upload a CSV file for processing. The uploaded data will be used for search and visualization.</p>
    """,
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader("Upload a CSV file:", type="csv")

data = None
if uploaded_file:
    # Load CSV file
    data = pd.read_csv(uploaded_file)
    st.markdown("### Preview of Uploaded CSV File:")
    st.dataframe(data, use_container_width=True)

# Processing Options
if data is not None:
    st.markdown("---")
    st.subheader("⚙️ Data Processing Options")
    st.markdown(
        """
        <p style="color: #444;">Select a column to process and choose an operation.</p>
        """,
        unsafe_allow_html=True,
    )
    primary_column = st.selectbox("Select the primary column to process", options=data.columns)
    process_option = st.selectbox("Choose processing type", ["None", "Summarize Data", "Retrieve Web Data"])

    if process_option == "Summarize Data":
        st.write(f"### Summary of {primary_column}:")
        st.write(data[primary_column].describe())
    elif process_option == "Retrieve Web Data":
        search_query = st.text_input(
            "Enter search query (use {entity} for entity placeholder):",
            value="What is {entity}",
        )
        if st.button("🚀 Start Web Search"):
            st.subheader("🔍 Web Search Results")
            st.markdown(
                "<p style='color: #444;'>Fetching results from the web. Please wait...</p>",
                unsafe_allow_html=True,
            )

            # Remove duplicates before processing
            unique_entities = data[primary_column].drop_duplicates().tolist()  # Ensure unique queries only
            results = []

            # Process only unique entities
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

                # Append each result to the results list
                results.append({"Query": query, "Response": summary})

            # Convert results to a DataFrame
            results_df = pd.DataFrame(results)

            # Avoid displaying duplicates by iterating through unique results
            unique_results = results_df.drop_duplicates(subset=["Response"])
            for _, result in unique_results.iterrows():
                st.markdown(
                    f"""
                    <div style="background-color: #F2F3F4; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #2E86C1;">
                        <p><strong>Query:</strong> {result["Query"]}</p>
                        <p><strong>Response:</strong> {result["Response"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Add download button for results
            st.download_button(
                label="📥 Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name="web_search_results.csv",
                mime="text/csv",
            )

# Data Visualization Section with emoji
if data is not None:
    st.markdown("---")
    st.subheader("📊 Data Visualization")
    st.markdown(
        """
        <p style="color: #444;">Visualize your data using various chart types.</p>
        """,
        unsafe_allow_html=True,
    )
    chart_type = st.selectbox("Choose a chart type", ["None", "Bar Chart", "Line Chart", "Pie Chart"])
    if chart_type == "Bar Chart":
        st.bar_chart(data[primary_column].value_counts())
    elif chart_type == "Line Chart":
        st.line_chart(data[primary_column].value_counts())
    elif chart_type == "Pie Chart":
        fig, ax = plt.subplots()
        data[primary_column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

# Footer with better design
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; font-size: 0.9em; color: #888;">
        Developed by Shruthi. Powered by <span style="color: #007bff;">OpenAI</span> and 
        <span style="color: #FF4500;">SerpAPI</span>.
    </div>
    """,
    unsafe_allow_html=True,
)

