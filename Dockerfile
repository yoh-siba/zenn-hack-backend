FROM python:3.12-slim


WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 && apt-get clean

# Copy all code
COPY . /app

# Install Poetry
RUN pip install poetry

# Disable virtualenv creation
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies
RUN poetry install

# Set port for Cloud Run
ENV PORT=8080

# Run app directly without poetry
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]