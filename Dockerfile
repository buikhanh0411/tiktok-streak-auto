# Use official Playwright image which has all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Install system dependencies including libavif13 and xvfb
RUN apt-get update && apt-get install -y \
    libavif-dev \
    libavif13 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install browsers
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Create data directory for volumes
RUN mkdir -p data/config

# Ensure python can find the src module
ENV PYTHONPATH=/app

# Run the bot with xvfb-run on Linux to provide a virtual display
CMD ["xvfb-run", "--server-args=-screen 0 1920x1080x24", "python", "src/bot/main.py"]
