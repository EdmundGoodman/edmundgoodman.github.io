MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.DEFAULT_GOAL := install

.PHONY: install
install:
	uv sync

.PHONY: run
run:
	uv run download.py

.PHONY: check
check:
	uv run ruff check --fix download.py
	uv run ruff format download.py
	uv run ruff check download.py
	uv run mypy download.py

.PHONY: clean
clean:
	rm -rf .mypy_cache/ .ruff_cache/
	find . -not -path "./.venv/*" | \
		grep -E "(/__pycache__$$|\.pyc$$|\.pyo$$)" | \
		xargs rm -rf

.PHONY: clobber
clobber: clean
	rm uv.lock
	rm -rf .venv/
