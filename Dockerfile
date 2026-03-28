# Use Python 3.11 for a modern, stable Streamlit runtime
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for FPDF/Pillow and other media processing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the local requirements.txt to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Create the assets folder in case it was ignored
RUN mkdir -p assets

# Expose port 8080 (the default for Google Cloud Run)
EXPOSE 8080

# Configure Streamlit to run on port 8080
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
