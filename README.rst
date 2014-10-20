Embarrasingly distributed parallel loop
=======================================


Warnings: the package is still in development. Backward compatibility might
not be preserved.

Aims:  simple, pure python

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


Tips when working on supercomputer
----------------------------------
    - Refuse the temptation to guess: work with absolute path.
    - With multiple python interpreter, use absolute path to the desired python
      interpreter.
    - ``sys.executable`` will give you the current python interpreter.
    - If objects are hashed, hash them sooner rather than later.


TODO list
---------
    - Find a way to get job id / job name in a generic way
