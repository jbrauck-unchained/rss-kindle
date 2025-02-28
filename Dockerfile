# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy everything at once
COPY . .

# Install dependencies explicitly including uvicorn
RUN pip install --no-cache-dir fastapi uvicorn requests python-dotenv

# Make port 8000 available
EXPOSE 8000

# Use a direct command that doesn't rely on PATH
CMD ["/usr/local/bin/python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
