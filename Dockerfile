# Use the official Python image as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install

# Activate the virtual environment
RUN poetry env use python && poetry env activate

ENV PORT=8080

# Copy the rest of the application code to the container
COPY . /app
# Command to run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]

