FROM python:3.11-rc-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

USER root

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 5001

ENV LISTEN_PORT=5001

CMD ["uvicorn", "app:main", "--host=127.0.0.1", "--port=5001", "--workers=4"]