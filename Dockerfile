# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Expose port
EXPOSE 80

# Run the application
# Command to run locally
# uvicorn app.main:app 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
