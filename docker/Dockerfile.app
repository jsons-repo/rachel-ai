FROM python:3.10.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libportaudio2 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only what’s needed to install the app
COPY pyproject.toml ./
COPY src ./src

# Install the app and expose scripts
RUN pip install --no-cache-dir -e .

# Default entrypoint (can be overridden by docker-compose)
CMD ["start"]
