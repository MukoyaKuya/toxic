# Stage 1: Build Tailwind CSS
FROM node:20-slim AS node-builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY tailwind.config.js .
COPY web/static/css/input.css ./web/static/css/
COPY templates ./templates
COPY web/templates ./web/templates
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

COPY . .
# Copy generated CSS from builder stage
COPY --from=node-builder /app/web/static/css/output.css ./web/static/css/output.css

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "toxic_project.wsgi:application"]
