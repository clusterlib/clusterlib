"""
This module allows to load and store values using a simple sqlite database
in a distributed fashion.
"""

# Authors: Arnaud Joly
#
# License: BSD 3 clause

import os
import sqlite3
import pickle

__all__ = [
    "sqlite3_loads",
    "sqlite3_dumps",
]


# sqlite3 ---------------------------------------------------------------------

def sqlite3_loads(file_name, key, timeout=7200.0):
    """Load value with key from sqlite3 stored at fname

    In order to improve performance, it's advised to
    query the database using a list of keys. Otherwise you might
    run into the `SQlite lock timeout
    <http://beets.radbox.org/blog/sqlite-nightmare.html>`_.

    Note if there is no sqlite3 database at ``file_name``,
    then an empty dictionnary is returned.

    Parameters
    ----------
    key : str or list of str
        Key used when the value was stored or list of keys.

    file_name : str
        Path to the sqlite database.

    timeout : float, (default=7200.0)
        The timeout parameter specifies how long the connection should wait
        for the lock to go away until raising an exception.

    Returns
    -------
    out : dict
        Return a dict where each key point is associated to the stored object.
        If a key from key is missing in the sqlite3, then there is no
        entry in out for this key.

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
    ...     print(out)
    ...
    {'3': 3}

    """
    if isinstance(key, str):
        key = [key]

    out = dict()
    if os.path.exists(file_name):
        with sqlite3.connect(file_name, timeout=timeout) as connection:
            cursor = connection.cursor()
            for k in key:
                cursor.execute("SELECT value FROM dict where key = ?", (k,))
                value = cursor.fetchone() # key is the primary key
                if value is not None:
                    out[k] = pickle.loads(bytes(value[0]))

            cursor.close()


    return out


def _compressed(value):
    """Compressed binary object with highest pickle protocol for sqlite3"""
    return sqlite3.Binary(pickle.dumps(value,
                                       protocol=pickle.HIGHEST_PROTOCOL))


def sqlite3_dumps(dictionnary, file_name, timeout=7200.0):
    """Dumps value with key in the sqlite3 database

    Parameters
    ----------
    fname : str
        Path to the sqlite database.

    dictionnary: dict of (str, object)
        Each key is a string associated to an object to store in the database,
        it will raise an exception if the key is already present in the
        database.

    timeout : float, (default=7200.0)
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
