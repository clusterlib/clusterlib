Embarrasingly distributed parallel loop
=======================================

.. image:: https://secure.travis-ci.org/clusterlib/clusterlib.png?branch=master
   :target: https://secure.travis-ci.org/clusterlib/clusterlib
   :alt: Build status

.. image:: https://coveralls.io/repos/clusterlib/clusterlib/badge.png?branch=master
   :target: https://coveralls.io/r/clusterlib/clusterlib
   :alt: Coverage status


Warnings: the package is still in development. Backward compatibility might
not be preserved.

Aims:  simple, pure python

This library works well with `joblib <https://pythonhosted.org/joblib/>`_,
which is intended to solve similar issues in shared memory architecture.


Getting the latest code
-----------------------

To get the latest code using git, simply type:

    git clone git://github.com/clusterlib/clusterlib.git

If you don't have git installed, you can download a zip or tarball of the
latest code: https://github.com/clusterlib/clusterlib/archive/master.zip


Installing
----------

As any Python packages, to install clusterlib, simply do:

    python setup.py install

in the source code directory.

How to contribute?
------------------

To contribute to clusterlib, first create a github account. Then you can
fork the `clusterlib repository <https://github.com/clusterlib/clusterlib>`_.
Once this is done, you can make clone of your fork, make your changes and
whenever you are happy, send us a pull request to the main repository.

Running the test suite
----------------------

To run the test suite, you need nosetests and the coverage modules.
Run the test suite using::

    nosetests

from the root of the project.


Documentation
-------------

For making the documentation, Sphinx==1.2.2 and sphinx-bootstrap-theme==0.4.0
are needed. Then, you can do

    make doc

To update the documentation on http://clusterlib.github.io/clusterlib/, simply
do

    make gh-pages
