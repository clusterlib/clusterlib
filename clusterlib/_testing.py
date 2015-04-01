"""Utilities for testing

Note: this module has a dependency on the nose package.

"""
# Authors: Olivier Grisel
#
# License: BSD 3 clause
import shutil
import os
import warnings
from tempfile import mkdtemp

from nose import SkipTest
from nose.tools import with_setup

from clusterlib.scheduler import _which

SHARED_TEST_FOLDER = os.environ.get('CLUSTERLIB_TEST_SHARED_FOLDER', '.')
DELETE_TEST_FOLDER = int(os.environ.get('CLUSTERLIB_DELETE_TEST_FOLDER', 1))
TEMP_FOLDER_PREFIX = "clusterlib_test_"


class TemporaryDirectory(object):
    """Create and return a temporary directory.

    This has the same behavior as mkdtemp but can be used as a context manager.
    For example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.

    Note: this class backported and adapted from the Python 3.4 stdlib for
    backward compat of the tests with Python 2.

    """
    # Handle mkdtemp raising an exception
    name = None
    _closed = False

    def __init__(self,
                 suffix="",
                 prefix=TEMP_FOLDER_PREFIX,
                 directory=SHARED_TEST_FOLDER,
                 delete_on_exit=DELETE_TEST_FOLDER):
        self.name = mkdtemp(suffix, prefix, directory)
        self.delete_on_exit = delete_on_exit

    @classmethod
    def _cleanup(cls, name, warn_message=None):
        shutil.rmtree(name)
        if warn_message is not None:
            warnings.warn(warn_message, ResourceWarning)

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        if self.delete_on_exit:
            self.cleanup()

    def cleanup(self):
        if self.name is not None and not self._closed:
            shutil.rmtree(self.name)
            self._closed = True


def _skip_if_no_backend():
    """Test decorator to skip test if no backend is available """

    # Note that we can't use _get_backend since the user might
    # have set the CLUSTERLIB_BACKEND environment variable.

    if _which('qmod') is None and _which('scontrol') is None:
        raise SkipTest('A scheduler backend is required for this test.')


skip_if_no_backend = with_setup(_skip_if_no_backend)
