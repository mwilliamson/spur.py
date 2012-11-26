.PHONY: test

test:
	nosetests -m'^$$' `find tests -name '*.py'`

upload:
	pandoc --from=markdown --to=rst README.md > README
	python setup.py sdist upload
	rm README
	rm MANIFEST
	rm -r dist
