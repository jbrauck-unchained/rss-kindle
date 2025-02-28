# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly install FastAPI and uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Copy the rest of the application
COPY . .

# Make port 8000 available
EXPOSE 8000

# Command to run the app
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
