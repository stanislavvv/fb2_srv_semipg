PYTHON=/usr/bin/python3
FLAKE8_ARGS=--max-line-length=120
PYLINT_ARGS=--max-line-length=120 --ignore-imports=yes --min-similarity-lines=8
MYPY_ARGS=--namespace-packages --ignore-missing-imports --strict
DATA=data
export FLASK_ENV=prod

help:
	@echo "Run \`make <target>'"
	@echo "Available targets:"
	@echo "  clean     - clean all"
	@echo "  cleandata - remove static pages"
	@echo "  flakeall  - check all .py by flake8"
	@echo "  lintall   - check all .py by pylint"
	@echo "  help      - this text"
	@echo "  update    - update data from .zip"

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '.mypy_cache' -print0 | xargs -0 -n1 rm -rf
	rm -rf venv

cleandata:
	rm -rf data/pages

flakeall:
	find . -not -path "./venv/*" -not -path "./tmp/*" -name '*.py' -print0 | xargs -0 -n 100 flake8 $(FLAKE8_ARGS)

lintall:
	find . -not -path "./venv/*" -not -path "./tmp/*" -name '*.py' -print0 | xargs -0 -n 100 pylint $(PYLINT_ARGS)

mypyall:
	find . -not -path "./venv/*" -not -path "./tmp/*" -name '*.py' -print0 | xargs -0 -n 1 mypy $(MYPY_ARGS)

update:
	@echo "------ lists ------"
	./datachew.sh new_lists
	@echo "------ data -----"
	./datachew.sh fillonly

venv:
	mkdir -p venv
	$(PYTHON) -m venv venv
	venv/bin/pip3 install -r requirements.txt
