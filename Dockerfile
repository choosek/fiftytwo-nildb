FROM python:3.11-slim-bullseye

WORKDIR /app
COPY app/ app/
COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app/app.py"]
