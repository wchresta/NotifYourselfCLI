.PHONY: all build install

PYTHON=/usr/bin/env python3
TWINE=/usr/bin/env twine

all: build

clean:
	rm -rf ./build
	rm -rf ./dist

build:
	${PYTHON} setup.py sdist bdist_wheel

testupload:
	${TWINE} upload --repository testpypi dist/*

upload:
	${TWINE} upload dist/*

install:
	${PYTHON} -m pip install --user .

