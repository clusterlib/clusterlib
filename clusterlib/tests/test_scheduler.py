# Authors: Arnaud Joly
#
# License: BSD 3 clause
from __future__ import unicode_literals

import os
import subprocess
from getpass import getuser
from xml.etree.ElementTree import XMLParser, XML

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
        if _which('scontrol'):
            # SLURM should be detected
            assert_equal(_get_backend('auto'), 'slurm')
        elif _which('qmod'):
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

    if (_which('qmod') is not None or
            _which('scontrol') is not None):
        raise SkipTest("This platform has either slurm or sge installed")

    assert_equal(queued_or_running_jobs(), [])


def check_job_name_queued_or_running_sge(job_name):
    # Check that SGE is installed
    if _which('qmod') is None:
        raise SkipTest("qmod (sge) is missing")

    user = getuser()
    # Launch a sleepy slurm job
    sleep_job = submit(job_command="sleep 600", job_name=job_name,
                       backend="sge", time="700", memory=100)

    # Encoding to UTF-8 is required when passing job_name with non-ASCII chars
    os.system(sleep_job.encode('utf-8'))

    # Get job id
    job_id = None
    try:
        out = subprocess.check_output(["qstat", "-xml", "-u", user, "-j",
                                       job_name])
        tree = XML(out, parser=XMLParser(encoding='utf-8'))
        for id_, name in zip(tree.iter("JB_job_number"),
                             tree.iter("JB_name")):
            if name.text == job_name:
                job_id = id_.text[0]
                break

    except subprocess.CalledProcessError as error:
        print(error.output)
        raise

    # Assert that the job has been launched
    try:
        running_jobs = queued_or_running_jobs(user=user)
        assert_in(job_name, running_jobs)
    finally:
        # Make sure to clean up even if there is a failure
        if job_id is not None:
            subprocess.call(["qdel", job_id])
        if os.path.exists("%s.%s" % (job_name, job_id)):
            os.remove("%s.%s" % (job_name, job_id))


def check_job_name_queued_or_running_slurm(job_name):
    """Test queued or running job function on slurm"""

    # Check that slurm is installed
    if _which('scontrol') is None:
        raise SkipTest("scontrol (SLURM) is missing")

    user = getuser()

    # Launch a sleepy slurm job
    sleep_job = submit(job_command="sleep 600", job_name=job_name,
                       backend="slurm", time="10:00", memory=100)

    # Encoding to UTF-8 is required when passing job_name with non-ASCII chars
    os.system(sleep_job.encode('utf-8'))

    # Get job id
    job_id = None
    try:
        out = subprocess.check_output(['squeue', '--noheader', '-o', '%j %i',
                                       '-u', user])
        for line in out.splitlines():
            name, id_ = line.decode("utf8").split()

            if job_name == name:
                job_id = id_
                break

    except subprocess.CalledProcessError as error:
        print(error.output)
        raise

    # Assert that the job has been launched
    try:
        running_jobs = queued_or_running_jobs(user=user)
        assert_in(job_name, running_jobs)
    finally:
        # Make sure to clean up even if there is a failure
        if job_id is not None:
            subprocess.call(["scancel", job_id])

        if os.path.exists("slurm-%s.out" % job_id):
            os.remove("slurm-%s.out" % job_id)


def test_queued_or_running_jobs():
    """Test queued or running job function on sge and slurm"""

    for job_name in ["test-sleepy-job", u'test-unicode-sl\xe9\xe9py-job']:
        yield check_job_name_queued_or_running_sge, job_name
        yield check_job_name_queued_or_running_slurm, job_name


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
        '-l h_rt=24:00:00 -l h_vmem=4000M -j y '
        '-o path/test/$JOB_NAME.$JOB_ID.txt')

    assert_equal(
        submit(job_command="python main.py", log_directory="path/test",
               backend="slurm"),
        "echo \'#!/bin/bash\npython main.py\' | sbatch --job-name=job "
        "--time=24:00:00 --mem=4000 -o path/test/job.%j.txt")

    assert_raises(ValueError, submit, job_command="", backend="unknown")
