# Compila o programa principal e os testes unitários

# Python settings
PYTHON := python3
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/Scripts
VENV_ACTIVATE := $(VENV_BIN)/activate

# Requirements
REQUIREMENTS := requirements.txt

# Source files
MAIN := main.py
SRC := $(wildcard *.py)

.PHONY: all venv install run clean lint test docs

all: venv install run

# Create virtual environment
venv:
	$(PYTHON) -m venv $(VENV_NAME)

# Install dependencies
install: venv
    $(VENV_BIN)/pip install -r $(REQUIREMENTS)

# Run the program
run:
    $(VENV_BIN)/python $(MAIN)

# Clean up generated files and virtual environment
clean:
    rm -rf $(VENV_NAME)
    rm -rf __pycache__
    rm -rf *.pyc
    rm -rf .pytest_cache
    rm -rf build dist *.egg-info

# Lint the code
lint:
    $(VENV_BIN)/pip install pylint
    $(VENV_BIN)/pylint $(SRC)

# Run tests (placeholder)
test:
    $(VENV_BIN)/pip install pytest
    $(VENV_BIN)/pytest

# Generate documentation (placeholder)
docs:
    $(VENV_BIN)/pip install pdoc
    $(VENV_BIN)/pdoc --html --output-dir docs $(SRC)

# Create requirements.txt
requirements:
    $(VENV_BIN)/pip freeze > $(REQUIREMENTS)