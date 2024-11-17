# **QueryScope AI**

Empowering data search and visualization with AI. This project provides a user-friendly dashboard for uploading CSV files, running web searches, and visualizing data insights interactively.

---

## **Table of Contents**
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**
- **Data Upload**: Easily upload CSV files for processing.
- **Web Search**: Leverage SerpAPI and OpenAI for web searches, delivering ChatGPT-style results.
- **Data Visualization**: Visualize data insights using Bar, Line, and Pie charts.
- **Download Results**: Export processed data and search results as a CSV file.
- **Professional UI**: Clean and attractive user interface with intuitive navigation.
- **Streamlined Workflow**: Processes data with unique response handling and avoids duplicates.

---

## **Installation**

Follow these steps to set up and run the project on your local machine:

### **1. Clone the Repository**
```bash
git clone https://github.com/shruthii05/AI-Agent-Project.git
cd AI-Agent-Project
 ```


### **2. Set Up a Virtual Environment**
```bash
python3 -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up API Keys**
Add your OpenAI and SerpAPI API keys to your Streamlit secrets:
```bash
[openai]
api_key = "your_openai_api_key"

[serpapi]
api_key = "your_serpapi_api_key"
```
### **5. Run the Application**
```bash
streamlit run app.py
```

## **Usage**

### **Uploading a CSV File**
- Drag and drop a CSV file into the "Upload Your Data" section.
- Preview your data and select a column to process.

### **Performing Web Searches**
- Choose **"Retrieve Web Data"** in the processing options.
- Enter a query template (e.g., **"What is {entity}?"**).
- Click **Start Web Search** to fetch search results.

### **Visualizing Data**
- Select a chart type (**Bar, Line, or Pie Chart**).
- View interactive visualizations of your dataset.

### **Downloading Results**
- After web searches, click **Download Results as CSV** to export the processed data.

## **Screenshots**

### **Homepage**
<img width="1674" alt="image" src="https://github.com/user-attachments/assets/48cbc76b-9d19-4fc0-9090-cf29868cda87">

### **Web Search Results**
<img width="1674" alt="image" src="https://github.com/user-attachments/assets/f77d3add-c275-44d2-acf0-4fd85d14b16d">

### **Data Visualization**
<img width="1674" alt="image" src="https://github.com/user-attachments/assets/d7afdf3d-17af-41ef-9cfc-2be677a048e9">

## **Contributing**
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch 
   ```bash
   git checkout -b feature-name
   ```
3. Commit your Changes
    ```bash
   git commit -m "Added new feature"
    ```
4. Push to the Branch
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request


## **License**
This project is licensed under the MIT License. You’re free to use, modify, and distribute it as per the terms of the license.

## **Credits**
This project uses the following technologies and libraries:

- **Streamlit**
- **OpenAI API**
- **SerpAPI**
- **Pandas**
- **Matplotlib**






