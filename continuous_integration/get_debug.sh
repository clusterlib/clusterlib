#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

# License: 3-clause BSD


set -xe # Exit on first error

#cat /var/spool/gridengine/qmaster/messages
find /var/spool/gridengine -name "messages" |xargs cat
ls -lR /var/spool/gridengine
#exit (1)