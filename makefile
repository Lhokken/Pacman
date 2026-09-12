PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

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
	@echo "* venv        : Create virtual environment                 *"
	@echo "* clean       : Remove cache                               *"
	@echo "* lint        : Run flake8 and mypy                        *"
	@echo "* lint-strict : Run mypy --strict                          *"
	@echo "*__________________________________________________________*"
	@echo "\n"

venv:
	python3 -m venv .venv
	@echo ""
	@echo "Virtualenv creato in .venv"
	@echo "Per attivarlo esegui: source .venv/bin/activate"
	@echo ""

install:
	$(PYTHON) -m pip install -r requirements.txt
	@if ls packaging/mazegenerator*.whl 1> /dev/null 2>&1; then \
		echo "Installing A-maze-ing wheel..."; \
		$(PYTHON) -m pip install packaging/mazegenerator*.whl; \
	elif ls packaging/mazegenerator*.zip 1> /dev/null 2>&1; then \
		echo "Installing A-maze-ing zip..."; \
		$(PYTHON) -m pip install packaging/mazegenerator*.zip; \
	elif [ -d packaging/mazegenerator* ] && ( [ -f packaging/mazegenerator*/setup.py ] || [ -f packaging/mazegenerator*/pyproject.toml ] ); then \
		echo "Installing A-maze-ing from source directory..."; \
		$(PYTHON) -m pip install -e packaging/mazegenerator*/; \
	else \
		echo "WARNING: No installable A-maze-ing package found in packaging/. Skipping."; \
	fi

run:
	$(PYTHON) pac-man.py config.json

debug:
	$(PYTHON) -m pdb pac-man.py config.json

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: help install run debug venv clean lint lint-strict