.. currentmodule:: clusterlib

.. _changes_dev:


dev
===

Changelog
---------

    - Add travis build for continous integration. By `Arnaud Joly`_

    - Add the possibility to get all key-value pairs from the sqlite3 database
      with :func:`storage.sqlite3_loads` by spetting ``key`` to ``None``.
      By `Arnaud Joly`_

    - Add a :func:`storage.sqlite3_loads` and :func:`storage.sqlite3_dumps`
      to work cache easily results of functions or scripts in distributed
      environments. By `Arnaud Joly`_

    - Add a :func:`scheduler.queued_or_running_jobs` function to get the names
      of all running jobs on SGE or SLURM cluster. By `Arnaud Joly`_

    - Add a :func:`scheduler.submit` function to write easily job submission
      query to sun grid engines (SGE) and SLURM. By `Arnaud Joly`_


.. _Arnaud Joly: http://www.ajoly.org

