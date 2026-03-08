# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g. for sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt ./backend/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Environment variable for port
ENV PORT=8080

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
