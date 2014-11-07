# clusterlib_launcher.py

import sys
import os
from clusterlib.scheduler import queued_or_running_jobs
from clusterlib.scheduler import submit
from clusterlib.storage import sqlite3_loads
from clusterlib_main import NOSQL_PATH

if __name__ == "__main__":
    scheduled_jobs = set(queued_or_running_jobs())
    done_jobs = sqlite3_loads(NOSQL_PATH)

    for param in range(100):
        job_name = "job-param=%s" % param
        job_command = "%s clusterlib.py --param %s" % (sys.executable,
                                                       param)

        if job_name not in scheduled_jobs and job_command not in done_jobs:
            script = submit(job_command, job_name=job_name)
            print(script)

            # Uncomment this line to launch the jobs
            # os.system(script)
