==========
User guide
==========

This documentation aims at showing how to use python and :mod:`clusterlib` to
launch and manage jobs on super-computer with scheduler such as SLURM or SGE.

Typically working on a super-computer requires to maintain and to write
three programs:

1. A *main program* who performs some useful computations and accept some
   parameters.
2. A *submission script*, e.g. a bash script, where you define the resource
   needed by the jobs such the maximal duration and the maximal required
   memory.
3. A *launching script* which will coordinate your submission scripts and
   and *main program* to perform all the required computations.

In the following, we will see how to use Python to manage a large number of
jobs without actually needing any submission script and avoiding to re-launch
job that are queued, running or already done.

How to submit easily a job?
---------------------------



How to avoid re-launching queued or running jobs?
-------------------------------------------------


How to avoid re-launching already done jobs?
--------------------------------------------

Using the storage module or joblib.call_and_shelve


A full fledge scikit-learn example
----------------------------------



More tips when working on supercomputer
---------------------------------------

- Refuse the temptation to guess: work with absolute path.
- With multiple python interpreters, use absolute path to the desired python
  interpreter. ``sys.executable`` will give you the current python interpreter.
- If objects are hashed, hash them sooner rather than later.
- Check the logic your programs with a fast and dummy setting.
