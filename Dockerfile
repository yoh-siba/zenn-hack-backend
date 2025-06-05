# Use the official Python image as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the rest of the application code to the container
COPY . /app



# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install

# Activate the virtual environment
RUN poetry env use python && poetry env activate

ENV PORT=8080
# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

