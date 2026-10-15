UV := uv
PYTHON := .venv/bin/python

.DEFAULT_GOAL := help
help:
	@echo "\n"
	@echo "_\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/_"
	@echo "*                                                          *"
	@echo "*                   Available targets                      *"
	@echo "*__________________________________________________________*"
	@echo "*                                                          *"
	@echo "* Available targets:                                       *"
	@echo "*                                                          *"
	@echo "* install     : Install dependencies                       *"
	@echo "* run         : Run Simulation                             *"
	@echo "* debug       : Run with pdb                               *"
	@echo "* uv          : Create virtual environment                 *"
	@echo "* clean       : Remove cache                               *"
	@echo "* lint        : Run flake8 and mypy                        *"
	@echo "* lint-strict : Run mypy --strict                          *"
	@echo "*__________________________________________________________*"
	@echo "\n"

uv:
	$(UV) venv .venv
	@echo ""
	@echo "Virtualenv creato in .venv con uv"
	@echo "Per attivarlo esegui: source .venv/bin/activate"
	@echo ""

install:
	uv sync --project .
	@wheel=$$(find packaging -maxdepth 1 -type f -name 'mazegenerator*.whl' -print -quit); \
	if [ -n "$$wheel" ]; then \
		uv pip install --python .venv/bin/python "$$wheel"; \
	else \
		archive=$$(find packaging -maxdepth 1 -type f -name 'mazegenerator*.zip' -print -quit); \
		if [ -z "$$archive" ]; then \
			echo "ERROR: No A-Maze-ing package found in packaging/."; \
			exit 1; \
		fi; \
		tmpdir=$$(mktemp -d); \
		trap 'rm -rf "$$tmpdir"' EXIT; \
		unzip -q "$$archive" '*.whl' -d "$$tmpdir"; \
		wheel=$$(find "$$tmpdir" -type f -name 'mazegenerator*.whl' -print -quit); \
		if [ -z "$$wheel" ]; then \
			echo "ERROR: No A-Maze-ing wheel found inside $$archive."; \
			exit 1; \
		fi; \
		uv pip install --python .venv/bin/python "$$wheel"; \
	fi

run:
	$(PYTHON) pac-man.py config.json

debug:
	$(PYTHON) run python -m pdb pac-man.py config.json

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache

lint:
	$(UV) run --group dev flake8 .
	$(UV) run --group dev mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run --group dev flake8 .
	$(UV) run --group dev mypy . --strict

.PHONY: help install run debug uv clean lint lint-strict
