# Use official Playwright image which has all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

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

# Run the bot
CMD ["python", "src/bot/main.py"]
