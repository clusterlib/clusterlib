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

def sqlite3_loads(fname, key, timeout=7200.0):
    """Load value with key from sqlite3 stored at fname

    In order to improve improve performance, it's advised to
    query the database using a list of keys. Otherwise you might
    run into the `SQlite lock timeout
    <http://beets.radbox.org/blog/sqlite-nightmare.html>`_

    Note if there is no sqlite3 database at fname, then None is return for
    each key.

    Parameters
    ----------
    fname : str
        Path to the sqlite database

    key : str or list of str
        Key used when the value was stored.

    timeout : float, (default=7200.0)
        The timeout parameter specifies how long the connection should wait
        for the lock to go away until raising an exception.

    Returns
    -------
    out : dict
        Return a dict where each key point is associated to the stored object.
        If the key is missing, there is no key for this entry in out

    """
    if isinstance(key, str):
        key = [key]

    out = dict()
    if os.path.exists(fname):
        with sqlite3.connect(fname, timeout=timeout) as connection:
            cursor = connection.cursor()
            for k in key:
                cursor.execute("SELECT value FROM dict where key = ?", (k,))
                value = cursor.fetchone() # key is the primary key
                if value is not None:
                    out[k] = pickle.loads(bytes(value[0]))

            cursor.close()

    return out


def sqlite3_dumps(fname, key, value, timeout=7200.0):
    """Dumps value with key in the sqlite3 database

    Parameters
    ----------
    fname : str
        path to the sqlite database

    key : str
        Key to the object.  If the key is already present in the database, it
        will raise an exception

    value : object
        Object to stored

    timeout : float, (default=7200.0)
        The timeout parameter specifies how long the connection should wait
        for the lock to go away until raising an exception.

    """
    value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    with sqlite3.connect(fname, timeout=timeout) as connection:
        # Create table if needed
        connection.execute("""CREATE TABLE IF NOT EXISTS dict
                              (key TEXT PRIMARY KEY, value BLOB)""")

        # Add a new key
        connection.execute("INSERT INTO dict(key, value) VALUES (?, ?)",
                           (key, sqlite3.Binary(value)))
