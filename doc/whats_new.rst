.. currentmodule:: clusterlib

.. _changes_dev:


dev
===

Changelog
---------

    - Add a :func:`storage.sqlite3_loads` and `storage.sqlite3_dump`
      to work cache easily results of functions or scripts in distributed
      environments. By `Arnaud Joly`_

    - Add a :func:`scheduler.queued_or_running_jobs` function to get the names
      of all running jobs on SGE or SLURM cluster. By `Arnaud Joly`_

    - Add a :func:`scheduler.submit` function to write easily job submission
      query to sun grid engines (SGE) and SLURM. By `Arnaud Joly`_


.. _Arnaud Joly: http://www.ajoly.org

