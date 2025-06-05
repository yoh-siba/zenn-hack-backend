# Use the official Python image as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi --no-root

# Activate the virtual environment
RUN poetry env use python && echo "$(poetry env info --path)" > /venv_path

# Set the virtual environment path
ENV VIRTUAL_ENV=/venv_path
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the rest of the application code to the container
COPY . /app
COPY src /app/src

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
