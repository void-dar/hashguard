FROM python:3.12-slim

# Install poetry
ENV POETRY_VERSION=2.1.0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

# Copy dependency files first (layer cache)
COPY pyproject.toml poetry.lock* ./

# Install only production deps
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Copy application source
COPY hashguard/ ./hashguard/

# Expose port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
