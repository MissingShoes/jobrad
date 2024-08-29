FROM python:3.12-slim

# Install PostgreSQL client libraries and other dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    build-essential


# setup poetry
RUN pip install poetry==1.8.2 && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

WORKDIR /app
COPY . .

RUN poetry install --no-interaction

ENV PYTHONPATH=/app
ENV PATH=/app/.venv/bin:$PATH

CMD ["hypercorn", "--bind", "0.0.0.0:8080", "--workers", "1", "chat_service/asgi:app"]
