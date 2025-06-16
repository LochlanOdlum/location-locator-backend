# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory into the container
COPY ./app ./app
COPY ./db_data_seeding ./db_data_seeding

# Expose port FastAPI will run on
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
