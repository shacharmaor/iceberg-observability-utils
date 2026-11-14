# Collector image. Runs under OpenShift's restricted policy: arbitrary non-root UID, group 0,
# group-writable directories, port above 1024. Build against the internal mirror:
#   docker build --build-arg PYTHON_IMAGE=<registry>/python:3.13-slim \
#                --build-arg PIP_INDEX_URL=<mirror>/simple -t iceobs-collector collector
ARG PYTHON_IMAGE=python:3.13-slim
FROM ${PYTHON_IMAGE}

ARG PIP_INDEX_URL=""
ENV PIP_INDEX_URL=${PIP_INDEX_URL} PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 HOME=/tmp

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY tools ./tools
RUN pip install --no-cache-dir . \
    && chgrp -R 0 /app && chmod -R g=u /app

# No fixed UID: OpenShift assigns one. Numeric non-root user so the image also runs elsewhere.
USER 1001:0
EXPOSE 8080
CMD ["python", "-m", "iceobs_collector"]
