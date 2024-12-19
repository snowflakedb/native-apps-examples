FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/ .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run" , "main.py", "--server.port=8501", "--server.address=0.0.0.0" ]
