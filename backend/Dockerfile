# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY ./requirements.txt .
RUN pip install --prefer-binary --no-cache-dir -r requirements.txt

# Copy the entire app directory into the container
COPY ./app ./app
COPY ./scripts ./scripts

# Expose port FastAPI will run on
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["sh", "-c", "python scripts/db_data_seeding/seed_script.py && python scripts/cloudflare-update.py && gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 app.main:app"]
