FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY src/ src/
COPY data/ data/

RUN uv sync --no-dev

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "mdf.remote"]
