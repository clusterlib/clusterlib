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

elif [[ "$SCHEDULER" == "SGE" ]]; then
    # The following lines are taken from BSD 3 project from
    # https://github.com/drmaa-python/drmaa-python

    cd continuous_integration/sge

    sudo sed -i -r "s/^(127.0.0.1\s)(localhost\.localdomain\slocalhost)/\1localhost localhost.localdomain $(hostname) /" /etc/hosts
    sudo apt-get update -qq
    echo "gridengine-master shared/gridenginemaster string localhost" | sudo debconf-set-selections
    echo "gridengine-master shared/gridenginecell string default" | sudo debconf-set-selections
    echo "gridengine-master shared/gridengineconfig boolean true" | sudo debconf-set-selections
    sudo apt-get install gridengine-common gridengine-master
    # Do this in a separate step to give master time to start
    sudo apt-get install libdrmaa1.0 gridengine-client gridengine-exec
    export CORES=$(grep -c '^processor' /proc/cpuinfo)
    sed -i -r "s/template/$USER/" user_template
    sudo qconf -Auser user_template
    sudo qconf -au $USER arusers
    sudo qconf -as localhost
    export LOCALHOST_IN_SEL=$(qconf -sel | grep -c 'localhost')
    if [ $LOCALHOST_IN_SEL != "1" ]; then sudo qconf -Ae host_template; else sudo qconf -Me host_template; fi
    sed -i -r "s/UNDEFINED/$CORES/" queue_template
    sudo qconf -Ap smp_template
    sudo qconf -Aq queue_template
    echo "Printing queue info to verify that things are working correctly."
    qstat -f -q all.q -explain a
    echo "You should see sge_execd and sge_qmaster running below:"
    ps aux | grep "sge"

    cd ../..

    export SGE_ROOT=/var/lib/gridengine
    export SGE_CELL=default
    export DRMAA_LIBRARY_PATH=/usr/lib/libdrmaa.so.1.0

 fi
