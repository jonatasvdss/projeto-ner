FROM python:3.10-slim-bookworm

WORKDIR /app

RUN apt update && \
    apt install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5058

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5058", "--timeout", "600000", "app:app"]