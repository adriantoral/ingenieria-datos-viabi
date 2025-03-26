FROM python:3.13-slim

WORKDIR /consumer

COPY pyproject.toml poetry.lock consumer/metadata/main.py ./
RUN pip install --no-cache-dir poetry && poetry install --no-root

CMD ["poetry", "run", "python", "main.py"]