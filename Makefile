dev:
	poetry run flask --app page_analyzer:app run

lint:
	poetry run flake8 page_analyzer

build:
	./build.sh

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

install:
	poetry install

reinstal:
	pip install --user --force-reinstall dist/*.whl

test:
	poetry run pytest

PORT ?= 8000

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app