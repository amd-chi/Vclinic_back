# Base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

ENV PYTHONBUFFERED=1

# Copy the requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .


# Command to run Django server
CMD ["gunicorn", "jahed_backend_api.wsgi:application", "--bind", "0.0.0.0:8000"]
