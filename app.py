import streamlit as st
import pandas as pd
import gspread
import matplotlib.pyplot as plt
from google.oauth2 import service_account

st.image("images/header_image.png", use_column_width=True)  # Display header image
st.title("AI Agent Dashboard")  # Title of your app
st.subheader("Simplifying Data Search and Analysis with AI")  # Subtitle for context

# Load credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# Authorize Google Sheets API client
try:
    client = gspread.authorize(credentials)
except Exception as e:
    st.error("🚨 Error authorizing Google Service Account credentials. Please check your Streamlit secrets.")
    st.stop()

# Apply Custom Style for Enhanced UI
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .block-container {
        max-width: 1200px;
        padding: 2rem 1rem;
    }
    h1, h2, h3 {
        font-weight: bold;
        color: #2c3e50;
    }
    .css-1d391kg {
        padding: 1.5rem;
    }
    .stButton>button {
        background-color: #2ecc71;
        color: white;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #27ae60;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# File Upload Section
st.markdown("### 📂 Upload or Connect Your Data")
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📥 Upload a CSV File", type="csv")
with col2:
    sheet_url = st.text_input("🌐 Enter Google Sheets URL (must be public)")

data = None

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.markdown("### 🔎 Preview of Uploaded CSV Data")
    st.write(data.head())
elif sheet_url:
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        records = sheet.get_all_records()
        data = pd.DataFrame(records)
        st.markdown("### 🔎 Preview of Google Sheets Data")
        st.write(data.head())
    except Exception as e:
        st.error(f"🚨 Error connecting to Google Sheets: {e}")

# Data Processing Section
if data is not None:
    st.markdown("---")
    st.markdown("### ⚙️ Data Processing Options")
    primary_column = st.selectbox("📊 Select the column for processing", options=data.columns)

    process_option = st.radio(
        "🔧 Choose Processing Type",
        ["None", "Summarize Data", "Retrieve Web Data"],
        horizontal=True,
    )

    if process_option == "Summarize Data":
        st.markdown("### 📈 Data Summary")
        st.write(data[primary_column].describe())

    elif process_option == "Retrieve Web Data":
        st.markdown("### 🔍 Web Search Results")
        search_query = st.text_input("🔎 Enter Search Query (use {entity} for placeholder)")
        if st.button("✨ Start Web Search"):
            results = []
            for entity in data[primary_column].unique():
                query = search_query.replace("{entity}", str(entity))
                # Placeholder result for demonstration
                results.append({"Entity": entity, "Query": query, "Result": "Sample Result"})
            results_df = pd.DataFrame(results)
            st.write(results_df)

            st.download_button(
                label="💾 Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name="search_results.csv",
                mime="text/csv",
            )

# Data Visualization Section
if data is not None:
    st.markdown("---")
    st.markdown("### 📊 Data Visualization")
    visualization_column = st.selectbox("📋 Select Column for Visualization", options=data.columns)
    chart_type = st.selectbox("📈 Choose a Chart Type", ["None", "Bar Chart", "Line Chart", "Pie Chart"])

    if chart_type == "Bar Chart":
        st.bar_chart(data[visualization_column].value_counts())
    elif chart_type == "Line Chart":
        st.line_chart(data[visualization_column].value_counts())
    elif chart_type == "Pie Chart":
        fig, ax = plt.subplots()
        data[visualization_column].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

# Footer with Emojis
st.markdown("---")
st.markdown(
    """
    <p style="text-align:center; color:#7f8c8d;">
        <strong>Developed by Shruthi 💡</strong> | Powered by <strong>OpenAI 🤖</strong> and <strong>SerpAPI 🌐</strong>
    </p>
    """,
    unsafe_allow_html=True,
)

