.PHONY: test upload clean bootstrap setup

test:
	sh -c '. _virtualenv/bin/activate; nosetests -m'\''^$$'\'' `find tests -name '\''*.py'\''`'
	
upload: setup
	python setup.py sdist upload
	make clean
	
register: setup
	python setup.py register

clean:
	rm -f MANIFEST
	rm -rf dist
	
bootstrap: _virtualenv
	_virtualenv/bin/pip install -e .
ifneq ($(wildcard test-requirements.txt),) 
	_virtualenv/bin/pip install -r test-requirements.txt
endif
	make clean

_virtualenv: 
	virtualenv _virtualenv
