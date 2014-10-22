# Authors: Arnaud Joly
#
# License: BSD 3 clause
from nose.tools import assert_equal
from nose.tools import assert_raises

from ..scheduler import queued_or_running_jobs
from ..scheduler import submit


def test_smoke_test():
    # XXX :  need a better way to test those functions
    queued_or_running_jobs()


def test_submit():
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
