# Gunakan base Python slim
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project ke container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port FastAPI
EXPOSE 8000

# Command untuk jalankan FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]