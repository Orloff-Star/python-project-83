install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

lint:
	poetry run flake8 page_analyzer

build:
	poetry build

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
