FROM python:3.11-slim

# Install Node.js 18 for frontend build
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build frontend
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm install

COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build into backend for serving
RUN cp -r frontend/build backend/

WORKDIR /app/backend

EXPOSE 8000

# Run migrations then start server
CMD alembic upgrade head 2>/dev/null; python -m app.seed 2>/dev/null; uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
