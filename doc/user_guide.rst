==========
User guide
==========

This documentation aims at showing how to use python and :mod:`clusterlib` to
launch and manage jobs on super-computers with schedulers such as
`SLURM <https://computing.llnl.gov/linux/slurm/>`_ or
`SGE <http://en.wikipedia.org/wiki/Oracle_Grid_Engine>`_.

Typically working on a super-computer requires to maintain and to write
three programs:

1. A *main program* who performs some useful computations and accept some
   parameters.
2. A *submission script*, e.g. a bash script, where you define the resources
   needed by the jobs such as the maximal duration and the maximal required
   memory.
3. A *launching script* which will coordinate your submission scripts and
   and the *main program* to perform all the required computations.

In the following, we will see how to use Python to manage a large number of
jobs without actually needing any submission script and avoiding to re-launch
queued, running or already completed jobs.


.. _submit_jobs:

How to submit jobs easily?
--------------------------

Submitting a job on a cluster requires to write a shell script to specify the
resources required for the job. For instance, here you have an example of
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
everything in Python without any of the previous drawbacks::

    >>> from clusterlib.scheduler import submit
    >>> script = submit("srun hostname", job_name="job-name",
    ...                 time="10:00", memory=1000, backend="slurm")
    >>> print(script)
    echo '#!/bin/bash
    srun hostname' | sbatch --job-name=job-name --time=10:00 --mem=1000

Launching the job with the generated submission ``script`` can be done
directly by using ``os.system(script.encode('utf-8'))`` or with the Python
``subprocess`` submodule.

Note that we explicitly encoded the script to `utf-8` before passing it to
`os.system`. This is required if you pass a `command` or `job_name`
with non-ASCII characters.

More options to the submission script could be appended to the generated
string. Here for instance, we add the quiet sbatch option::

    >>> script += ' --quiet'  # Note the space in front of --
    >>> print(script)
    echo '#!/bin/bash
    srun hostname' | sbatch --job-name=job-name --time=10:00 --mem=1000 --quiet

In the case your task required multiple lines, you can separate each command
by making a line break in the job command::

    >>> script = submit("srun hostname\nsleep 60", job_name="job-name",
    ...                 time="10:00", memory=1000, backend="slurm")
    >>> print(script)
    echo '#!/bin/bash
    srun hostname
    sleep 60' | sbatch --job-name=job-name --time=10:00 --mem=1000


How to avoid re-launching queued or running jobs?
-------------------------------------------------

In the previous section, we have seen how to write and generate submission
queries. This allows to schedule thousands of jobs with a simple logic. In order
to spare computing resources, we are going to add some mechanisms to avoid
launching jobs that are already queued or running.

The function :func:`clusterlib.scheduler.queued_or_running_jobs` allows to get
the list of all running or queued jobs. This will allow us to derive a first
launching manager. As a small usage example, here we want to launch the program
``main`` for a variety of parameters, while avoiding to re-relaunch jobs that
are already queued or running.

.. code-block:: python

    import os
    from clusterlib.scheduler import queued_or_running_jobs
    from clusterlib.scheduler import submit

    if __name__ == "__main__":
        scheduled_jobs = set(queued_or_running_jobs())
        for param in range(100):
            job_name = "job-param=%s" % param
            if job_name not in scheduled_jobs:
                script = submit("./main --param %s" % param,
                                job_name=job_name, backend="slurm")

                os.system(script.encode('utf-8'))

Here we have constructed unique job names with a string formatting. As an
alternative, one can generate hash of the job parameters to have automatically
unique identifiers using either the Python built-in ``hash`` or
`joblib.hash <https://pythonhosted.org/joblib/generated/joblib.hash.html>`_.


How to avoid re-launching already done jobs?
--------------------------------------------

Checking if a job is queued or running must be done through the scheduler.
However, knowing if a job is already done must be accomplished through the file
system. Clusterlib offers a simple NO-SQL database based on sqlite3 to achieve
this. With the transactions of the database, jobs could register their
completion.

Let's take a practical example, we want to launch the script ``main.py`` with a
large number of different parameter combinations. Due to the heavy
computational burden, we want to parallelize the script evaluation on a
super-computer.

.. literalinclude:: ../examples/simple-launcher/main.py

First, we modify or add to the original script some call to
the NO-SQL database which will indicate the parameter combinations that have
been evaluated.

.. literalinclude:: ../examples/simple-launcher/clusterlib_main.py

Secondly, we write a launcher script (``clusterlib_launcher.py``) to
use this information and re-launch only jobs that have not been done so far
or that are not running or queued.

.. literalinclude:: ../examples/simple-launcher/clusterlib_launcher.py

This simple launcher allows to manage thousands of jobs while avoiding
to repeat jobs that are processed or in process.


How to take advantage of scheduler logs in job management?
----------------------------------------------------------

Jobs that are sent to a cluster might fail due to programming errors or
to exceeding booked ressources (time, memory). Nevertheless, the scheduler
will report error traceback and might inform you of why your jobs has been
killed in a log file. With the :func:`clusterlib.scheduler.submit`,
job logs will be at specify directory with the format ``job_name.job_id.txt``
where the ``job_id`` is given by the scheduler.

For examples, we can take advantage of this log path normalisation by adding
debug options to our job management script.

.. code-block:: python

    import os
    import argparse
    from clusterlib.scheduler import submit

    LOG_DIRECTORY = "~/clusterlib_logs"

    if __name__ == "__main__":
        # Let's a debug option to this script
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--debug', default=False, action="store_true",
                            help="Display debug logs if any")
        args = vars(parser.parse_args())

        # Create the log directory if needed
        if not os.path.exists(LOG_DIRECTORY):
            os.makedirs(LOG_DIRECTORY)

        for param in range(100):
            job_name = "job-param=%s" % param
            script = submit("./main --param %s" % param,
                            job_name=job_name,
                            log_directory=LOG_DIRECTORY)

            if args["debug"]:  # Display logs if any
                os.system("cat %s"
                          % os.path.join(LOG_DIRECTORY, "%s.*.txt" % job_hash))

            os.system(script.encode('utf-8'))


The previous example can be enhanced by displaying only logs of jobs that
might have failed and by automatically increasing time and memory ressources
for jobs having been cancelled due hitting the limits.


Choosing the backend implementation
-----------------------------------

By default ``clusterlib`` will try to automatically detect the presence of the
scheduler commands in the following order:

- SLURM
- SGE

If both schedulers are installed on the cluster, it is possible to explicitly
pass ``backend='slurm'`` or ``backend='sge'`` to the ``submit`` function.

Alternatively it is also possible to set the default backend by setting the
``CLUSTERLIB_BACKEND`` environment variable, for instance by adding the
following line in the ``~/.bashrc`` file of the user that starts the job::

    export CLUSTERLIB_BACKEND=slurm


More tips when working on a super-computer
-----------------------------------------

- Forbid the temptation to guess: work with absolute path.
- With multiple python interpreters, use absolute path to the desired python
  interpreter. ``sys.executable`` will give you the path of the python
  interpreter.
- If objects are hashed, hash them sooner rather than later.
- Check your program logic with a fast and dummy setting.
- Use a version file system such as git.
