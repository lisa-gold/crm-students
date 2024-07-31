lint:
	poetry run flake8 crm

start:
	fastapi dev crm/app.py
