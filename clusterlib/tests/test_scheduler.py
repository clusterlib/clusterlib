# Authors: Arnaud Joly
#
# License: BSD 3 clause

from ..scheduler import queued_or_running_jobs


# XXX :  need a better way to test those functions

def test_smoke_test():
    queued_or_running_jobs()

