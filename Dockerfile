# ---- Backend ----
FROM python:3.11-slim AS backend

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

# ---- Frontend ----
FROM node:22-alpine AS frontend

WORKDIR /ui
COPY ui/package*.json ./
RUN npm install

COPY ui/ .
RUN npm run build

# ---- Final Image ----
FROM python:3.11-slim

WORKDIR /app

# backend
COPY --from=backend /app /app

# frontend static
COPY --from=frontend /ui/dist /app/ui

EXPOSE 8000

CMD ["python", "src/main.py"]