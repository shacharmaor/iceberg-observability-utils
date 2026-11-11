PY_PROJECTS := collector ui-backend

.PHONY: lint test

lint:
	@for p in $(PY_PROJECTS); do \
		(cd $$p && uv run ruff check . && uv run ruff format --check .) || exit 1; \
	done

test:
	@for p in $(PY_PROJECTS); do \
		(cd $$p && uv run pytest -q) || exit 1; \
	done
