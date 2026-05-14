FROM python:3.14.5 AS base

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

FROM base AS dev

COPY requirements-dev.txt .

RUN python -m pip install --no-cache-dir -r requirements-dev.txt

CMD ["fastapi", "dev", "src/generic_pdf_processor/main.py", "--host", "0.0.0.0", "--port", "4000"]

FROM dev AS test

CMD ["python", "-m", "pytest"]

FROM base AS prod

CMD ["fastapi", "run", "src/generic_pdf_processor/main.py", "--host", "0.0.0.0", "--port", "4000"]

EXPOSE 4000
