# Authors: Arnaud Joly
#
# License: BSD 3 clause
from __future__ import unicode_literals

import os
import subprocess
import sys
from getpass import getuser


from nose.tools import assert_equal
from nose.tools import assert_raises
from nose.tools import assert_in
from nose import SkipTest

from ..scheduler import queued_or_running_jobs
from ..scheduler import submit


def test_queued_or_running_jobs_slurm():
    """Test queued or running job function on slurm"""

    # Check that slurm is installed
    with open(os.devnull, 'w') as shutup:
        has_sbatch = 1 - subprocess.check_call(["which", "sbatch"],
                                               stdout=shutup, stderr=shutup)

        if not has_sbatch:
            raise SkipTest("sbatch is missing")


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
