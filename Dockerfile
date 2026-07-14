FROM python:3.13-slim

WORKDIR /workspace

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# HuggingFace cache
ENV HF_HOME=/model-cache

# Expose FastAPI
EXPOSE 8000

# Start application
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]