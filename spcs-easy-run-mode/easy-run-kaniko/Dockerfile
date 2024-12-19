# Use Kaniko executor as the base image
FROM gcr.io/kaniko-project/executor:v1.23.2 AS kaniko

# Install Python. Since Kaniko's base image is busybox, this step would typically involve
# installing from source or copying from another image. This example uses a two-stage build
# to copy Python from an chainguard Python image.

# Stage 1: Get Python from the chainguard Python Docker image
FROM artifactory.int.snowflakecomputing.com/development-chainguard-virtual/snowflake.com/python-fips:3.10-dev AS python-base

# Copy requirements file
#COPY env/requirements.txt requirements.txt
# Install required packages using pip
RUN pip install -U pip &&  pip install watchdog pyyaml
FROM artifactory.int.snowflakecomputing.com/development-chainguard-virtual/snowflake.com/python-fips:3.10 AS final
USER root

WORKDIR /app
ARG WORK_DIR=/app

COPY --from=kaniko /kaniko /kaniko

COPY --from=python-base /home/nonroot/.local/lib/python3.10/site-packages /home/nonroot/.local/lib/python3.10/site-packages
# Set working directory and python path to find the installed packages
ENV PATH=/usr/local/bin:$PATH
ENV PYTHONPATH=/home/nonroot/.local/lib/python3.10/site-packages
ENV DOCKER_CONFIG=/kaniko/.docker/

# Copy context and Python scripts
COPY *.py ${WORK_DIR}
COPY docker_template ${WORK_DIR}

USER root
CMD ["build.py"]