FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY src/ src/
COPY data/ data/
COPY scripts/ scripts/

RUN uv sync --no-dev

ENV PYTHONPATH=/app/src

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "mdf.remote"]
