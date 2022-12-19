PYTHON = python3
PIP = pip3

test:
	$(PYTHON) -m unittest tests/network_tests.py
	$(PYTHON) -m unittest tests/game_tests.py

install:
	$(PIP) install -r requirements.txt

clean:
	find . -name '*log*' -delete
	find . -name '*cache*' -delete

