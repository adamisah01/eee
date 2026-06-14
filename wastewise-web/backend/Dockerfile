FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE core.settings

WORKDIR /app

# Install system dependencies (PostGIS/psycopg2 requirements)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gdal-bin \
        libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Expose Django port
EXPOSE 8000
# Expose FastAPI port
EXPOSE 8001

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
