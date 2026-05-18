FROM python:3.10-slim
EXPOSE 8080
WORKDIR /app
COPY src/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/. .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]

