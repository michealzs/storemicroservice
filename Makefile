.PHONY: install run test seed up down logs tf-init tf-plan tf-apply fmt

install:
	pip install -e ".[test]"

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

seed:
	python -m scripts.seed

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f app

tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply
