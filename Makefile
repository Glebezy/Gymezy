.PHONY: test run

test:
	ENV=test python -m pytest

run:
	ENV=prod python app.py