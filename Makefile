install:
	poetry install

page-loader:
	poetry run page-loader --output page_loader/data https://httpbin.org
	
# https://bahna.land/ru/bolota/ekosistemnye-funktsii-bolot-i-ikh-degradatsiya-vsledstvie-melioratsii-i-torfodobychi

build:
	poetry build

package-install:
	pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader
	poetry run flake8 tests

test:
	poetry run pytest -v --cov=page_loader tests/ --cov-report xml

.PHONY: install build package-install lint page-loader test