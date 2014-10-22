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

        data = dict((str(i), i) for i in range(5))
        sqlite3_dumps(data, fname)

        for i in range(5):
            assert_equal(sqlite3_loads(fname, str(i)), {str(i): i})

        # List of key
        assert_equal(sqlite3_loads(fname, ["1", "3"]), {"1": 1, "3": 3})
        assert_equal(sqlite3_loads(fname), data)

        # Missing in the db
        assert_equal(sqlite3_loads(fname, "unkonwn"), dict())
        assert_equal(sqlite3_loads(fname, ["0", "unkonwn"]), {"0": 0})

        # Complex object
        complex_object = {
            "tuple": (3, 2, "a"),
            "set": set([2, 3]),
        }
        sqlite3_dumps({"complex": complex_object}, file_name=fname)
        assert_equal(sqlite3_loads(key="complex", file_name=fname),
                     {"complex": complex_object})

        # Try to insert object twice
        assert_raises(sqlite3.IntegrityError, sqlite3_dumps,
                      {"complex": complex_object}, fname)

        # Ensure that we can store None
        sqlite3_dumps({"None": None}, fname)
        assert_equal(sqlite3_loads(fname, ["None"]), {"None": None})

        # Ensure that keys are string
        assert_raises(TypeError, sqlite3_dumps, {None: None})
        assert_raises(TypeError, sqlite3_dumps, {5: None})
        assert_raises(TypeError, sqlite3_dumps, {(5, ): None})

        assert_equal(sqlite3_loads(fname, [None]), dict())
        assert_raises(Exception, sqlite3_loads, fname, [(5, )])
        assert_raises(TypeError, sqlite3_loads, fname, 5)

    # Without any sqlite 3 database
    assert_equal(sqlite3_loads(fname, "0"), dict())
    assert_equal(sqlite3_loads(fname, ["0", "1"]), dict())
