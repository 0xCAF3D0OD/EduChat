FROM python:3.12-bookworm

WORKDIR /app

COPY playwright/playwright_test.py .

RUN apt-get update && apt-get install -y xvfb

RUN pip install --upgrade pip "fastapi[standard]"

RUN pip install playwright==1.57.0 && \
    playwright install --with-deps
