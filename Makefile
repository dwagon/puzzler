tests: test

test:
	uv run pytest --cov-report term-missing --cov . tests/*.py
