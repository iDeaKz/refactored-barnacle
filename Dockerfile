# Dockerfile

FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY app /app

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "api.__init__:app", "--host", "0.0.0.0", "--port", "8000"]
