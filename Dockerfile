FROM python:3.9-slim

# Install system dependencies required by Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Start the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

