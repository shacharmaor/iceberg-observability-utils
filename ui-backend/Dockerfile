# UI Backend image; same OpenShift-restricted conventions as the Collector image.
ARG PYTHON_IMAGE=python:3.13-slim
FROM ${PYTHON_IMAGE}

ARG PIP_INDEX_URL=""
ENV PIP_INDEX_URL=${PIP_INDEX_URL} PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 HOME=/tmp

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . \
    && chgrp -R 0 /app && chmod -R g=u /app

USER 1001:0
ENV ICEOBS_HTTP_PORT=8000
EXPOSE 8000
CMD ["python", "-m", "iceobs_ui_backend"]
