# Use the official Python 3.9 slim image as the base image
# You can adjust the Python version if needed
FROM python:3.9-slim

# Set the working directory inside the container
# All paths will be relative to this directory
WORKDIR /app

# Copy the requirements.txt file from the host to the working directory in the container
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
# The --no-cache-dir option ensures that pip doesn't cache the downloaded packages, keeping the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the host to the container
# This includes all files in the current directory, which may include source code, config files, etc.
COPY . .

# Expose port 8000 to the outside world
# FastAPI runs on port 8000 by default, and this will map the container's port 8000 to the host machine
EXPOSE 8000

# Command to run the FastAPI application with Uvicorn
# - "api.main:app" specifies the FastAPI app located in the `main.py` file inside the `api` folder
# - "--host 0.0.0.0" makes the server accessible on all network interfaces
# - "--port 8000" ensures the app runs on port 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
