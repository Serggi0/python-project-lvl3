install:
	poetry install

page-loader:
	poetry run page-loader --output page_loader/data http://vospitatel.com.ua/zaniatia/rastenia/lopuh.html
	
# http://vospitatel.com.ua/zaniatia/rastenia/lopuh.html
	
# https://zakupator.com/sad/chubushnik.html


# https://en.wikipedia.org/wiki/Correction_fluid
# https://www.google.ru 
# http://oldmuzzle.ru/flora/taraxacum-officinale.html
	
# https://animaljournal.ru/article/koshka_ocelot
# https://linzi-vsem.ru/karnavalnye/linzy-sharingan/
# https://ru.hexlet.io/courses
# https://httpbin.org

build:
	poetry build

package-install:
	pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader
	poetry run flake8 tests

test:
	poetry run pytest -v -s  --cov=page_loader tests/ 
# --cov-report xml

.PHONY: install build package-install lint page-loader test