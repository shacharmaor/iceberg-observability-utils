PY_PROJECTS := collector ui-backend

# Image build knobs: point these at the internal registry and mirrors inside the air gap.
IMAGE_REGISTRY ?=
PYTHON_IMAGE   ?= python:3.13-slim
NODE_IMAGE     ?= node:22
NGINX_IMAGE    ?= nginxinc/nginx-unprivileged:stable
PIP_INDEX_URL  ?=
NPM_REGISTRY   ?=

.PHONY: lint test build dev-up dev-down

lint:
	@for p in $(PY_PROJECTS); do \
		(cd $$p && uv run ruff check . && uv run ruff format --check .) || exit 1; \
	done

test:
	@for p in $(PY_PROJECTS); do \
		(cd $$p && uv run pytest -q) || exit 1; \
	done

build:
	docker build --build-arg PYTHON_IMAGE=$(PYTHON_IMAGE) --build-arg PIP_INDEX_URL=$(PIP_INDEX_URL) \
		-t $(IMAGE_REGISTRY)iceobs-collector:dev collector
	docker build --build-arg PYTHON_IMAGE=$(PYTHON_IMAGE) --build-arg PIP_INDEX_URL=$(PIP_INDEX_URL) \
		-t $(IMAGE_REGISTRY)iceobs-ui-backend:dev ui-backend
	docker build --build-arg NODE_IMAGE=$(NODE_IMAGE) --build-arg NGINX_IMAGE=$(NGINX_IMAGE) \
		--build-arg NPM_REGISTRY=$(NPM_REGISTRY) -t $(IMAGE_REGISTRY)iceobs-web-ui:dev web-ui

# One command: build our images, bring the stack up, seed Tables. Web UI: http://localhost:8081
dev-up: build
	docker compose -f deploy/dev/compose.yaml up -d

dev-down:
	docker compose -f deploy/dev/compose.yaml down -v
