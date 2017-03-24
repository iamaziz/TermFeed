

help:
	cat Makefile

install:
	pip install .

.PHONY: tests
tests:
	nosetests tests/

feed:
	python -m feed

bumpversion_patch:
	bumpversion patch

bumpversion_minor:
	bumpversion minor

bumpversion_mayor:
	bumpversion mayor
