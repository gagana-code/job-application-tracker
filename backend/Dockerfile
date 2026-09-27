# official Python image
FROM python:3.10-slim

# working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port (local/docker-compose default; see PORT below for hosted platforms)
EXPOSE 8000

# Run the application. Render (and most PaaS providers) inject a PORT env
# var and expect the app to bind to it; shell form lets us expand it with a
# local fallback of 8000 for docker-compose / plain `docker run`.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]