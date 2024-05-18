install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C app.py

docker-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile
format:
	black *.py

test:
	python -m pytest -vv tests/test_app.py
