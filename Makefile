.PHONY: test unit_test perf_test coverage lint doc

test:
	pytest

unit_test:
	pytest -m "not perf"

perf_test:
	pytest -m "perf"

coverage:
	coverage run -m pytest
	coverage report -m

lint:
	ruff check .

doc:
	pdoc3 --html --force --output-dir docs triangulator