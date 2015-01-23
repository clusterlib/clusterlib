#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

# License: 3-clause BSD


set -e # Exit on first error

# Install dependency for full test
pip install coverage coveralls
pip install sphinx_bootstrap_theme


if [[ "$SCHEDULER" == "SLURM" ]]; then
    sudo apt-get install slurm-llnl
    sudo /usr/sbin/create-munge-key
    sudo service munge start
    sudo python continuous_integration/configure_slurm.py
fi
