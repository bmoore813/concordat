test:
	docker build --tag concordat:latest .
	docker run concordat:latest pytest /concordat
