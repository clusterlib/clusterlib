# Authors: Arnaud Joly
#
# License: BSD 3 clause

import sqlite3
from tempfile import NamedTemporaryFile

from nose.tools import assert_equal
from nose.tools import assert_raises

from ..storage import sqlite3_loads
from ..storage import sqlite3_dumps


def test_sqlite3_storage():
    with NamedTemporaryFile() as fhandle:
        fname = fhandle.name

        for i in range(5):
            sqlite3_dumps(fname, str(i), i)

        for i in range(5):
            assert_equal(sqlite3_loads(fname, str(i)), {str(i): i})

        # List of key
        assert_equal(sqlite3_loads(fname, ["1", "3"]), {"1": 1, "3": 3})

        # Missing in the db
        assert_equal(sqlite3_loads(fname, "unkonwn"), dict())
        assert_equal(sqlite3_loads(fname, ["0", "unkonwn"]), {"0": 0})

        # Complex object
        complex_object = {
            "tuple": (3, 2, "a"),
            "set": set([2, 3]),
        }
        sqlite3_dumps(fname, "complex", complex_object)
        assert_equal(sqlite3_loads(fname, "complex"),
                     {"complex": complex_object})

        # Try to insert object twice
        assert_raises(sqlite3.IntegrityError, sqlite3_dumps,
                      fname, "complex", complex_object)

    # Without any sqlite 3 database
    assert_equal(sqlite3_loads(fname, "0"), dict())
    assert_equal(sqlite3_loads(fname, ["0", "1"]), dict())

