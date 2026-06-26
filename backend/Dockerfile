FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the worker script by default (we will change this to run both FastAPI and the worker later)
CMD ["python", "-u", "app/worker.py"]