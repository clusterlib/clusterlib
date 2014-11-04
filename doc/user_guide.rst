==========
User guide
==========

This documentation aims at showing how to use python and :mod:`clusterlib` to
launch and manage jobs on super-computer with schedulers such as SLURM or SGE.

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
queued, running or already done jobs.


.. _submit_jobs:

How to submit job easily?
-------------------------

Submitting a job on a cluster requires to write a shell script to specify the
resource required by the job. For instance, here you have an example of
a submission script using the
`SLURM sbatch command <https://computing.llnl.gov/linux/slurm/sbatch.html>`_
which scheduled a job requiring at most 10 minutes of computation and 1000 mega
bytes of ram.

.. code-block:: bash

    #!/bin/bash
    #
    #SBATCH --job-name=job-name
    #SBATCH --time=10:00
    #SBATCH --mem=1000

    srun hostname

Managing such scripts has several drawbacks: (i) a separate file has to be
maintained, (ii) parameters and resources are fixed in the script, e.g. memory
asked can not be adapted automatically given some parameter of the main program
and (iii) those scripts are scheduler specific.

With the :func:`clusterlib.scheduler.submit` function, you can simply do
without any the previous drawback::

    >>> from clusterlib.scheduler import submit
    >>> script = submit("srun hostname", job_name="job-name",
    ...                 time="10:00", memory=1000, backend="slurm")
    >>> print(script)
    echo '#!/bin/bash
    srun hostname' | sbatch --job-name=job-name --time=10:00 --mem=1000

Launching the job with the generated submission ``script`` can be done using
``os.system(script)`` or with the Python ``subprocess`` submodule.

More options to the submission script could be done by appending those. Here
for instance, we add the quiet sbatch option::

    >>> script += ' --quiet'  # Note the space in front of --
    >>> print(script)
    echo '#!/bin/bash
    srun hostname' | sbatch --job-name=job-name --time=10:00 --mem=1000 --quiet

For multi-line tasks, one can add the proper line break character
in the job command::

    >>> script = submit("srun hostname\nsleep 60", job_name="job-name",
    ...                 time="10:00", memory=1000, backend="slurm")
    >>> print(script)
    echo '#!/bin/bash
    srun hostname
    sleep 60' | sbatch --job-name=job-name --time=10:00 --mem=1000

How to avoid re-launching queued or running jobs?
-------------------------------------------------

In the previous section, we have seen how to write and generate submission
queries. This allows to schedule thousands of jobs with simple logic. In order
to spare computing resources, we are going to add some mechanism to avoid
launching jobs that are already queued or running.

The function :func:`clusterlib.scheduler.queued_or_running_jobs` allows
to get the list of all running or queued jobs. This will allow us to deverive
a first launching manager. Here we want to launch the program ``main``

.. code-block:: python

    import os
    from clusterlib.scheduler import queued_or_running_jobs
    from clusterlib.scheduler import submit

    jobs = set(queued_or_running_jobs())
    for param in range(10, 20, 3):
        job_name = "job-param=%s" % param
        if job_name not in jobs:
            script = submit("./main --param %s" % param,
                            job_name=job_name, backend="slurm")

            os.system(script)



How to avoid re-launching already done jobs?
--------------------------------------------

Using the storage module or the joblib.call_and_shelve


A full fledge scikit-learn example
----------------------------------



More tips when working on supercomputer
---------------------------------------

- Refuse the temptation to guess: work with absolute path.
- With multiple python interpreters, use absolute path to the desired python
  interpreter. ``sys.executable`` will give you the current python interpreter.
- If objects are hashed, hash them sooner rather than later.
- Check the logic your programs with a fast and dummy setting.
