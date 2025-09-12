FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create .env file with default values
RUN echo "SECRET_KEY=django-insecure-change-me-in-production" > .env
RUN echo "DEBUG=1" >> .env
RUN echo "DB_HOST=db" >> .env
RUN echo "DB_NAME=credit_approval_db" >> .env
RUN echo "DB_USER=postgres" >> .env
RUN echo "DB_PASSWORD=postgres" >> .env

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
