.. currentmodule:: clusterlib

.. _changes_dev:


dev
===

Changelog
---------
    - Add a travis workers with SLURM. By `Arnaud Joly`_ and
      `Olivier Grisel`_.

    - Add a travis workers with SGE. By `Arnaud Joly`_

    - Fix possible deadlock occurence due to the use ``subprocess.PIPE``.
      By `Arnaud Joly`_

    - Add the possibility to specify a user in
      :func:`scheduler.queued_or_running_jobs`. By `Arnaud Joly`_

    - Automate the detection of the scheduler based on the commands available
      in the ``PATH`` with ``backend='auto'`` (enabled by default).
      By `Olivier Grisel`_

    - Make `queued_or_running_jobs` return decoded job names (unicode strings
      instead of byte strings). By `Olivier Grisel`_

0.1
===

Changelog
---------

    - Add support for landscape.io to track code quality. By `Arnaud Joly`_

    - Add support for coveralls to track code coverage. By `Arnaud Joly`_

    - Add a user guide. By `Arnaud Joly`_

    - Add a travis bot for continous integration. By `Arnaud Joly`_

    - Add the possibility to get all key-value pairs from the sqlite3 database
      with :func:`storage.sqlite3_loads` by setting ``key`` to ``None``.
      By `Arnaud Joly`_

    - Add a :func:`storage.sqlite3_loads` and :func:`storage.sqlite3_dumps`
      to cache easily results of functions or scripts in distributed
      environments. By `Arnaud Joly`_

    - Add a :func:`scheduler.queued_or_running_jobs` function to get the names
      of all running jobs on SGE or SLURM cluster. By `Arnaud Joly`_

    - Add a :func:`scheduler.submit` function to write easily job submission
      query to sun grid engines (SGE) and SLURM. By `Arnaud Joly`_


.. _Arnaud Joly: http://www.ajoly.org

.. _Olivier Grisel: http://ogrisel.com
