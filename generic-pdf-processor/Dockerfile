FROM python:3.14.5 AS base

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip config set global.cache-dir /root/.cache/pip && \
    pip install -r requirements.txt

COPY . .

FROM base AS dev

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "4000"]

FROM base AS prod

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "4000"]

EXPOSE 4000