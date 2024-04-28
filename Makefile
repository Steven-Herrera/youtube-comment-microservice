install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

install-amazon-linux:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=R,C app.py

format:
	black *.py

test:
	python -m pytest -vv tests/test_app.py