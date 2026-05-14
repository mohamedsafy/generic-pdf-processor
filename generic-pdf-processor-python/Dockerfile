FROM python:3.14.5-alpine3.22 AS base

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip config set global.cache-dir /root/.cache/pip && \
    pip install -r requirements.txt

COPY . .

FROM base AS dev

COPY requirements-dev.txt .

RUN pip install -r requirements-dev.txt

CMD ["fastapi", "dev", "src/generic_pdf_processor/main.py", "--host", "0.0.0.0", "--port", "4000"]

FROM dev AS test

CMD ["python", "-m", "pytest"]

FROM base AS prod

CMD ["fastapi", "run", "src/generic_pdf_processor/main.py", "--host", "0.0.0.0", "--port", "4000"]

EXPOSE 4000
