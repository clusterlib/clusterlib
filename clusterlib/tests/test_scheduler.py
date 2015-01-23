# Authors: Arnaud Joly
#
# License: BSD 3 clause
from __future__ import unicode_literals

import os
import subprocess
import sys
from getpass import getuser
from xml.etree import ElementTree

from nose.tools import assert_equal
from nose.tools import assert_raises
from nose.tools import assert_in
from nose import SkipTest

from ..scheduler import queued_or_running_jobs
from ..scheduler import submit
from ..scheduler import _which
from ..scheduler import _get_backend


def test_auto_backend():
    """Check the backend detection logic"""
    original_env_backend = os.environ.get('CLUSTERLIB_BACKEND', None)
    if original_env_backend is not None:
        del os.environ['CLUSTERLIB_BACKEND']
    try:
        # Check detection when no environment variable is set.
        if _which('sbatch'):
            # SLURM should be detected
            assert_equal(_get_backend('auto'), 'slurm')
        elif _which('qsub'):
            # SGE should be detected
            assert_equal(_get_backend('auto'), 'sge')
        else:
            # No backend can be detected
            assert_raises(RuntimeError, _get_backend, 'auto')

        # Check the use of the environment variable
        os.environ['CLUSTERLIB_BACKEND'] = 'slurm'
        assert_equal(_get_backend('auto'), 'slurm')

        os.environ['CLUSTERLIB_BACKEND'] = 'sge'
        assert_equal(_get_backend('auto'), 'sge')
    finally:
        # Restore the previous environment
        if original_env_backend is None:
            del os.environ['CLUSTERLIB_BACKEND']
        else:
            os.environ['CLUSTERLIB_BACKEND'] = original_env_backend


def test_fixed_backend():
    """Check that it is possible to fix explicit backends (when valid)"""
    # Supported backends
    assert_equal(_get_backend('slurm'), 'slurm')
    assert_equal(_get_backend('sge'), 'sge')

    # Unsupported backend
    assert_raises(ValueError, _get_backend, 'hadoop')


def test_queued_or_running_jobs_no_backend():

    if (_which('qsub') is not None and
            _which('sbatch') is not None):
        raise SkipTest("This platform has either slurm or sge installed")

    assert_equal(queued_or_running_jobs(), [])


def test_queued_or_running_jobs_sge():
    """Test queued or running job function on sge"""
    # Check that slurm is installed
    if _which('qsub') is None:
        raise SkipTest("qsub (sge) is missing")

    user = getuser()
    job_name = "test-sleepy-job"

    # Launch a sleepy slurm job
    sleep_job = submit(job_command="sleep 600", job_name=job_name,
                       backend="sge", time="700", memory=100)
    os.system(sleep_job)

   # Get job id
    job_id = None
    try:
        out = subprocess.check_output("qstat -xml -u {0}".format(user),
            shell=True)
        tree = ElementTree.fromstring(out)
        job_id = [id_.text
                   for id_, name in  zip(tree.iter("JB_job_number"),
                                         tree.iter("JB_name"))
                   if name.text == job_name]
        job_id = job_id[0]

    except subprocess.CalledProcessError as error:
        print(error.output)
        raise

    # Assert that the job has been launched
    try:
        running_jobs = queued_or_running_jobs(user=user)
        assert_in(job_name, running_jobs)
    finally:
        # Make sure to clean up even if there is a failure
        os.system("qdel %s" % job_id)
        if os.path.exists("%s.%s" % (job_name, job_id)):
            os.remove("%s.%s" % (job_name, job_id))


def test_queued_or_running_jobs_slurm():
    """Test queued or running job function on slurm"""

    # Check that slurm is installed
    if _which('sbatch') is None:
        raise SkipTest("sbatch (SLURM) is missing")

    user = getuser()
    job_name = "test-sleepy-job"

    # Launch a sleepy slurm job
    sleep_job = submit(job_command="sleep 600", job_name=job_name,
                       backend="slurm", time="10:00", memory=100)
    os.system(sleep_job)

    # Get job id
    job_id = None
    try:
        out = subprocess.check_output(
            "squeue --noheader -o '%j %i' -u {0} | grep {1}"
            "".format(user, job_name),
            shell=True)
        job_id = out.split()[-1]

    except subprocess.CalledProcessError as error:
        print(error.output)
        raise

    # Assert that the job has been launched
    try:
        running_jobs = queued_or_running_jobs(user=user)
        if sys.version_info[0] == 3:
            # the bytes should be decoded before, right after you read them
            # (e.g. from a socket or a file). In Python 2 is done
            # implicitly with a random (platform specific) encoding.
            # In Python 3 youhave to decode bytes objects into unicode
            # string explicitly with an appropriate encoding depending on
            # where the bytes come from.

            running_jobs = [s.decode("utf8") for s in running_jobs]

        assert_in(job_name, running_jobs)
    finally:
        # Make sure to clean up even if there is a failure
        os.system("scancel %s" % job_id)
        if os.path.exists("slurm-%s.out" % job_id):
            os.remove("slurm-%s.out" % job_id)


def test_submit():
    """Test submit formatting function"""
    assert_equal(
        submit(job_command="python main.py", backend="sge"),
        'echo \'#!/bin/bash\npython main.py\' | qsub -N "job" -l '
        'h_rt=24:00:00 -l h_vmem=4000M')

    assert_equal(
        submit(job_command="python main.py", backend="slurm"),
        "echo '#!/bin/bash\npython main.py' | sbatch --job-name=job "
        "--time=24:00:00 --mem=4000")

    assert_equal(
        submit(job_command="python main.py", email="test@test.com",
               email_options="beas", backend="sge"),
        'echo \'#!/bin/bash\npython main.py\' | qsub -N "job" '
        '-l h_rt=24:00:00 -l h_vmem=4000M -M test@test.com -m beas')

    assert_equal(
        submit(job_command="python main.py", log_directory="path/test",
               backend="sge"),
        'echo \'#!/bin/bash\npython main.py\' | qsub -N "job" '
        '-l h_rt=24:00:00 -l h_vmem=4000M -o path/test/$JOB_NAME.$JOB_ID')

    assert_equal(
        submit(job_command="python main.py", log_directory="path/test",
               backend="slurm"),
        "echo \'#!/bin/bash\npython main.py\' | sbatch --job-name=job "
        "--time=24:00:00 --mem=4000 -o path/test/job.txt")

    assert_raises(ValueError, submit, job_command="", backend="unknown")
