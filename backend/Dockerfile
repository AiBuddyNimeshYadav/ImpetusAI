FROM python:3.11-slim

WORKDIR /app

# Install system deps for sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY backend/pyproject.toml .
COPY backend/app/ app/
COPY backend/demo_policies/ demo_policies/
COPY ai/ ../ai/

# Set working directory to install backend using relative path
RUN pip install --no-cache-dir -e ../ai
RUN pip install --no-cache-dir -e .

ENV PYTHONPATH=/app/..


# Create directories
RUN mkdir -p uploads chroma_data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
