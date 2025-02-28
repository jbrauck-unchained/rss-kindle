# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly install uvicorn to ensure it's available
RUN pip install --no-cache-dir uvicorn

# Make sure pip executables are in PATH
ENV PATH="/usr/local/bin:${PATH}"

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Command to run the FastAPI app using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
