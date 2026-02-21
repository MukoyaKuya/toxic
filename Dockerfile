# Stage 1: Build Tailwind CSS
FROM node:20-slim AS node-builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY tailwind.config.js .
COPY web/static/css/input.css ./web/static/css/
COPY templates ./templates
# Create empty python files to satisfy tailwind content scan if needed, or just copy structure
COPY toxic_project ./toxic_project
COPY web ./web
RUN npm run build

# Stage 2: Run Python App
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory so Django file handler init doesn't crash
RUN mkdir -p /app/logs

COPY . .
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
# Copy generated CSS from builder stage
COPY --from=node-builder /app/web/static/css/output.css ./web/static/css/output.css

# Collect static files into /app/staticfiles (served by whitenoise)
# SECRET_KEY, DATABASE_URL, and ALLOWED_HOSTS are only needed to pass settings.py checks at build time
ARG BUILD_SECRET_KEY=build-time-placeholder-key-not-used-in-prod
RUN SECRET_KEY=${BUILD_SECRET_KEY} \
    DATABASE_URL=sqlite:////tmp/db.sqlite3 \
    ALLOWED_HOSTS=localhost \
    DEBUG=0 \
    python manage.py collectstatic --noinput

ENTRYPOINT ["/docker-entrypoint.sh"]
