FROM python:3.10-slim-bookworm@sha256:5be5aaecb962a41567bc8041f1e9e3432cb085b037fe057f9a562630b2e4b370
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8081
WORKDIR /app
COPY src/requirements.txt .
RUN python -m pip install --require-hashes --only-binary=:all: --no-cache-dir -r requirements.txt
RUN useradd --uid 10001 --create-home appuser
COPY --chown=10001:10001 src/. .
RUN chmod +x ./entrypoint.sh
USER appuser
ENTRYPOINT ["./entrypoint.sh"]
