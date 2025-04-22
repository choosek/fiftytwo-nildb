FROM python:3.11-slim-bullseye

WORKDIR /app
COPY app/ app/
COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
    make build-essential gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# TODO: make run port configurable
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "app.app:app"]
