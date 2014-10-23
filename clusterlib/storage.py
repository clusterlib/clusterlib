"""
This module allows to load and store values using a simple sqlite database
in a distributed fashion. This is a simple `key-value NoSQL
<http://en.wikipedia.org/wiki/NoSQL>`_ database using only the Python standard
library and `sqlite3 <http://www.sqlite.org/>`_.

This can be used to cache results of functions or scripts in distributed
environments.

"""
# Authors: Arnaud Joly
#
# License: BSD 3 clause
from __future__ import unicode_literals

import os
import sqlite3
import pickle

__all__ = [
    "sqlite3_loads",
    "sqlite3_dumps",
]


def _decompressed(value):
    """Decompressed a binary object compressed with pickle from sqlite3"""
    return pickle.loads(bytes(value))


def _compressed(value):
    """Compressed binary object with highest pickle protocol for sqlite3"""
    return sqlite3.Binary(pickle.dumps(value,
                                       protocol=pickle.HIGHEST_PROTOCOL))


def sqlite3_loads(file_name, key=None, timeout=7200.0):
    """Load value with key from sqlite3 stored at fname

    In order to improve performance, it's advised to
    query the database using a (small) list of keys. Otherwise by calling
    this functions repeatedly, you might run into the `SQlite lock timeout
    <http://beets.radbox.org/blog/sqlite-nightmare.html>`_.

    Parameters
    ----------
    file_name : str
        Path to the sqlite database.

    key : str or list of str or None, optional (default=None)
        Key used when the value was stored or list of keys. If None, all
        key, value pair from the database are returned.

    timeout : float, optional (default=7200.0)
        The timeout parameter specifies how long the connection should wait
        for the lock to go away until raising an exception.

    Returns
    -------
    out : dict
        Return a dict where each key point is associated to the stored object.
        If a key from key is missing in the sqlite3, then there is no
        entry in out for this key. If there is no sqlite3 database at
        ``file_name``, then an empty dictionary is returned.

    Examples
    --------
    Here, we generate a temporary sqlite3 database, dump then load some
    data from it.

    >>> from tempfile import NamedTemporaryFile
    >>> from clusterlib.storage import sqlite3_dumps
    >>> from clusterlib.storage import sqlite3_loads
    >>> with NamedTemporaryFile() as fhandle:
    ...     sqlite3_dumps({"3": 3, "2": 5}, fhandle.name)
    ...     out = sqlite3_loads(fhandle.name, key=["7", "3"])
    ...     print(out['3'])
    ...     print("7" in out)  # "7" is not in the database
    3
    False

    It's also possible to get all key-value pairs from the database without
    specifying the keys.

    >>> with NamedTemporaryFile() as fhandle:
    ...     sqlite3_dumps({'first': 1}, fhandle.name)
    ...     out = sqlite3_loads(fhandle.name)
    ...     print(out['first'])
    1

    """
    if isinstance(key, str):
        key = [key]

    out = dict()
    if os.path.exists(file_name):
        if key is None:
            with sqlite3.connect(file_name, timeout=timeout) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT key, value FROM dict")
                out = cursor.fetchall()
                cursor.close()
            out = dict((key, _decompressed(value)) for key, value in out)

        else:
            with sqlite3.connect(file_name, timeout=timeout) as connection:
                cursor = connection.cursor()
                for k in key:
                    cursor.execute("SELECT value FROM dict where key = ?",
                                   (k,))
                    value = cursor.fetchone()  # key is the primary key
                    if value is not None:
                        out[k] = _decompressed(bytes(value[0]))

                cursor.close()

    return out


def sqlite3_dumps(dictionnary, file_name, timeout=7200.0):
    """Dumps value with key in the sqlite3 database

    Parameters
    ----------
    dictionnary: dict of (str, object)
        Each key is a string associated to an object to store in the database,
        it will raise an exception if the key is already present in the
        database.

    fname : str
        Path to the sqlite database.

    timeout : float, optional (default=7200.0)
        The timeout parameter specifies how long the connection should wait
        for the lock to go away until raising an exception.

    Examples
    --------
    Here, we generate a temporary sqlite3 database, then dump some data in it.

    >>> from tempfile import NamedTemporaryFile
    >>> from clusterlib.storage import sqlite3_dumps
    >>> from clusterlib.storage import sqlite3_loads
    >>> with NamedTemporaryFile() as fhandle:
    ...     sqlite3_dumps({"list": [3, 2], "number": 5}, fhandle.name)
    ...

    """
    # compressed value first
    compressed_dict = {k: _compressed(v) for k, v in dictionnary.items()}

    with sqlite3.connect(file_name, timeout=timeout) as connection:
        # Create table if needed
        connection.execute("""CREATE TABLE IF NOT EXISTS dict
                              (key TEXT PRIMARY KEY, value BLOB)""")

        # Add a new key
        connection.executemany("INSERT INTO dict(key, value) VALUES (?, ?)",
                               compressed_dict.items())
