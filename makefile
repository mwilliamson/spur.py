.PHONY: test upload clean bootstrap

test:
	sh -c '. _virtualenv/bin/activate; nosetests -m'\''^$$'\'' `find tests -name '\''*.py'\''`'
	
upload:
	tox
	_virtualenv/bin/python setup.py sdist bdist_wheel upload
	make clean
	
register:
	python setup.py register

clean:
	rm -f MANIFEST
	rm -rf dist build
	
bootstrap: _virtualenv
	_virtualenv/bin/pip install -e .
ifneq ($(wildcard test-requirements.txt),) 
	_virtualenv/bin/pip install -r test-requirements.txt
endif
	make clean

_virtualenv: 
	python3 -m venv _virtualenv
	_virtualenv/bin/pip install --upgrade pip
	_virtualenv/bin/pip install --upgrade setuptools
	_virtualenv/bin/pip install --upgrade wheel
