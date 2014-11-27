# Author: Arnaud Joly

all: clean inplace test

clean:
	python setup.py clean

in: inplace

inplace:
	python setup.py build_ext --inplace

test:
	nosetests clusterlib doc

doc: inplace
	$(MAKE) -C doc html

clean-doc:
	rm -rf doc/_build
	rm -rf doc/generated

view-doc: doc
	open doc/_build/html/index.html

gh-pages:
	git checkout master
	make doc
	rm -rf ../clusterlib-doc
	cp -a doc/_build/html ../clusterlib-doc
	git checkout gh-pages
	cp -a ../clusterlib-doc/* .
	echo 'Add new file to git'
	git add `ls ../clusterlib-doc`
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
	git push origin gh-pages
	git checkout master

