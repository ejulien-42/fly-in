PYTHON = python3
MAIN   = fly-in.py

.PHONY: install run debug clean lint lint-strict all

all: run

install:
	uv sync

run:
	uv run python3 -m src

debug:
	uv run python3 -m pdb -m src

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf .venv

lint:
	uv run python3 -m flake8 src
	uv run python3 -m mypy src \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
