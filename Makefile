init:
	pip install -r requirements.txt

test:
	python3 tests/AllTestsSuite.py

.PHONY: init test
