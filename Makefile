
test: install
	@env/bin/nosetests --with-coverage --cover-package=jsonmapping --cover-erase

install: env/bin/python upgrade

env/bin/python:
	virtualenv env
	env/bin/pip install --upgrade pip
	env/bin/pip install wheel nose coverage unicodecsv python-dateutil

upgrade:
	env/bin/pip install -e .

upload: install
	env/bin/python setup.py sdist bdist_wheel upload

clean:
	rm -rf env
