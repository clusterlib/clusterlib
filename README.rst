Embarrasingly distributed parallel loop
=======================================


Warnings: the package is still in development. Backward compatibility might
not be preserved.

Aims:  simple, pure python

This library works well with `joblib <https://pythonhosted.org/joblib/>`_,
which is intended to solve similar issue in shared memory architecture.


Getting the latest code
-----------------------

To get the latest code using git, simply type:

    git clone git://github.com/clusterlib/clusterlib.git

If you don't have git installed, you can download a zip or tarball of the
latest code: http://github.com/clusterlib/clusterlib/archive/master


Installing
----------

As any Python packages, to install clusterlib, simply do:

    python setup.py install

in the source code directory.

Running the test suite
=========================

To run the test suite, you need nosetests and the coverage modules.
Run the test suite using::

    nosetests

from the root of the project.

Documentation
-------------
For making the documentation, Sphinx==1.2.2 and sphinx-bootstrap-theme==0.4.0
are needed. Then, you can do

    make doc

Tips when working on supercomputer
----------------------------------
    - Refuse the temptation to guess: work with absolute path.
    - With multiple python interpreter, use absolute path to the desired python
      interpreter.
    - ``sys.executable`` will give you the current python interpreter.
    - If objects are hashed, hash them sooner rather than later.


TODO list
---------
    - Make a travis bot with slurm / sge
    - Add examples
