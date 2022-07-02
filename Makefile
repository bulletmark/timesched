NAME = $(shell basename $(CURDIR))

all:
	@echo "Type sudo make install|uninstall"
	@echo "or make sdist|upload|check|clean"

install:
	pip3 install -U --root-user-action=ignore .

uninstall:
	pip3 uninstall --root-user-action=ignore $(NAME)

sdist:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload: sdist
	twine3 upload --skip-existing dist/*

check:
	flake8 *.py
	vermin --no-tips -q *.py
	python3 setup.py check

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/
