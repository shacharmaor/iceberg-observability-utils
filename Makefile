.PHONY: lint test

lint:
	cd collector && uv run ruff check . && uv run ruff format --check .

test:
	cd collector && uv run pytest -q
