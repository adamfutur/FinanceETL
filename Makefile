# Finance ETL Hub - Project Management
# Usage: make <command>

PYTHON = python
PIP = pip

.PHONY: setup up down etl cdc test dashboard clean help

help:
	@echo "Finance ETL Hub - Commands:"
	@echo "  setup      - Install dependencies and create .env"
	@echo "  up         - Start PostgreSQL database (Docker)"
	@echo "  down       - Stop PostgreSQL database"
	@echo "  etl        - Run the full ETL pipeline"
	@echo "  cdc        - Run the CDC simulation (Initial + Incremental Load)"
	@echo "  predict    - Run AI Forecasting and Churn Analysis"
	@echo "  test       - Run unit tests with pytest"
	@echo "  dashboard  - Run the Streamlit dashboard"
	@echo "  clean      - Remove logs, cache, and temporary data"

setup:
	$(PIP) install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; fi

up:
	docker-compose up -d

down:
	docker-compose down

etl:
	$(PYTHON) main.py --step full

cdc:
	$(PYTHON) main.py --step cdc

predict:
	$(PYTHON) main.py --step predict

test:
	$(PYTHON) main.py --step test

dashboard:
	$(PYTHON) main.py --step dashboard

clean:
	@rm -rf logs/*
	@rm -rf data/processed/*
	@rm -rf .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleanup complete."
