FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update -y && apt-get install awscli -y && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
