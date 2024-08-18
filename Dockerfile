# Use an official Python 3.9 runtime as a parent image
FROM python:3.11-slim

# Set the working directory to the root of the project
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire content of the project into the container
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
