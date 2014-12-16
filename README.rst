Embarrasingly distributed parallel loop on clusters of computers
================================================================

.. image:: https://badge.fury.io/py/clusterlib.svg
    :target: http://badge.fury.io/py/clusterlib
    :alt: Pypi badge - latest release

.. image:: https://secure.travis-ci.org/clusterlib/clusterlib.png?branch=master
   :target: https://secure.travis-ci.org/clusterlib/clusterlib
   :alt: Build status

.. image:: https://coveralls.io/repos/clusterlib/clusterlib/badge.png?branch=master
   :target: https://coveralls.io/r/clusterlib/clusterlib
   :alt: Coverage status

.. image:: https://landscape.io/github/clusterlib/clusterlib/master/landscape.svg
   :target: https://landscape.io/github/clusterlib/clusterlib/master
   :alt: Code Health


The goal of this library is to ease the creation, launch and management of
embarassingly parallel jobs on supercomputer with schedulers such as `SLURM
<https://computing.llnl.gov/linux/slurm/>`_. Some basic primitives (e.g. pure
python NO-SQL database) are also provided to work in distributed memory
architecture.

Aims:  simple, pure python

If you want to parallelize your python jobs in shared memory architecture, I
advise you to use `joblib <https://pythonhosted.org/joblib/>`_.

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

How to make a release
---------------------
What follows is only for maintaners:

  1. Create a branch for the 0.X.Y version if necessary.
  2. Update What's new in the 0.X.Y version and master branch. Update version
     in the documentation at ``doc/conf.py``
  3. Make point the stable branch to 0.X.Y.
  4. Check the generated doc on read the doc for the stable and the 0.X.Y tag
     version.
  5. Check release on pypi test using

      python setup.py sdist upload -r pypitest

  6. Upload the new release on pypi using

     python setup.py sdist upload -r pypi
