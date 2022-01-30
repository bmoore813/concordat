test:
	docker build --tag concordat:latest .
	docker run concordat:latest pytest /concordat

purge-branches:
	git branch | grep -v "main" | xargs git branch -D

typecheck:
	mypy concordat/interface.py

lint:
	black .
	pylint concordat/interface.py

	
make-virtual:
	python3 -m venv venv   
	source venv/bin/activate 
	pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt