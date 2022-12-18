PYTHON = python3
PIP = pip3

test:
	$(PYTHON) -m unittest tests/network_tests.py

clean:
	find . -type d -name '*log*' -exec rm -r {} +
	find . -type d -name '*cache*' -exec rm -r {} +