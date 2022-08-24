# NOTE: Run in the src folder as context
FROM python:3.9-slim

# Install pre-requisites
COPY worker/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt && \
    mkdir /app
WORKDIR /app

# Install graphviz + other dependencies
RUN apt-get update && apt-get install graphviz -y

# DEBUG: Copy over dags folder for testing
RUN mkdir /dags && \
    mkdir /dags/inside
COPY dags/example_job.py /dags/example_job.py
COPY dags/inside/example_job_2.py /dags/inside/example_job_2.py

# Copy over src
COPY worker/celeryconfig.py .
COPY worker/config.py .
COPY worker/models.py .
COPY worker/utils.py .
COPY worker/modules.py .
COPY worker/main.py .

# ENTRYPOINT [ "python","-u","main.py" ]
# CMD [ "scheduler", "/dags" ]