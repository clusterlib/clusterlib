"""
Module to help working with scheduler such as sun grid engine (SGE) or
Simple Linux Utility for Resource Management (SLURM).

Main functions covered are :
    - get the list of names of all running jobs;
    - generate easily a submission query for a job.

"""

# Authors: Arnaud Joly
#
# License: BSD 3 clause

import subprocess
from xml.etree import ElementTree

__all__ = [
    "queued_or_running_jobs",
    "submit"
]


def _sge_queued_or_running_jobs():
    try:
        xml = subprocess.check_output("qstat -xml", shell=True,
                                      stderr=subprocess.PIPE)
        tree = ElementTree.fromstring(xml)
        return [leaf.text for leaf in tree.iter("JB_name")]
    except subprocess.CalledProcessError:
        # qstat is not available
        return []


def _slurm_queued_or_running_jobs():
    try:
        out = subprocess.check_output("squeue --noheader -o %j", shell=True,
                                      stderr=subprocess.PIPE)
        out = out.split("\n")[:-1]
        return out
    except subprocess.CalledProcessError:
        # squeue is not available
        return []


def queued_or_running_jobs():
    """Return the names of the queued or running jobs under SGE and SLURM

    The list of jobs could be either the list of all jobs on the scheduler
    or only the jobs associated to the user calling this function.
    The default behavior is dependant upon scheduler configuration.
    Try ``qstat`` in SGE or ``squeue`` in SLURM to know which behavior it
    follows.

    Returns
    -------
    out : list of string,
        Returned a list containing all the names of the jobs that are running
        or queued under the SGE or SLURM scheduler.

    """
    out = []
    for queued_or_running in (_sge_queued_or_running_jobs,
                              _slurm_queued_or_running_jobs):
        out.extend(queued_or_running())

    return out


_SGE_TEMPLATE = {
    "job_name": '-N "%s"',
    "memory": "-l h_vmem=%sM",
    "time": "-l h_rt=%s",
    "email": "-M %s",
    "email_options": "-m %s",
    "log_directory": "-o %s/$JOB_NAME.$JOB_ID",
}

_SLURM_TEMPLATE = {
    "job_name": '--job-name=%s',
    "memory": "--mem=%s",
    "time": "--time=%s",
    "email": "--mail-user=%s",
    "email_options": "--mail-type=%s",
    "log_directory": "-o %s/%s.txt",
}

_TEMPLATE = {
    "sge": _SGE_TEMPLATE,
    "slurm": _SLURM_TEMPLATE
}

_LAUNCHER = {
    "sge": "qsub",
    "slurm": "sbatch",
}


def submit(job_command, job_name="job", time="24:00:00", memory=4000,
           email=None, email_options=None, log_directory=None, backend="slurm",
           shell_script="#!/bin/bash"):
    """Write the submission query (without script)

    Parameters
    ----------
    job_command : str,
        Command associated to the job, e.g. 'python main.py'.

    job_name : str, optional (default="job")
        Name of the job.

    time : str, optional (default="24:00:00")
        Maximum time format "HH:MM:SS".

    memory : str, optional (default=4000)
        Maximum virtual memory in mega-bytes

    email : str, optional (default=None)
        Email where job information is sent. If None, no email is asked
        to be sent.

    email_options : str, optional (default=None)
        Specify email options:
            - SGE : Format char from beas (begin,end,abort,stop) for SGE.
            - SLURM : either BEGIN, END, FAIL, REQUEUE or ALL.
        See the documenation for more information

    log_directory : str, optional (default=None)
        Specify the log directory. If None, no log directory is specified.

    backend : {'sge', 'slurm'}, optional (default="slurm")
        Backend where the job will be submitted

    shell_script : str, optional (default="#!/bin/bash")
        Specify shell that is used by the script.

    Returns
    -------
    submission_query : str,
        Return the submission query in the appropriate format.
        The obtained query could be directly launch using os.subprocess.
        Further options could be appended at the end of the string.

    Examples
    --------
    First, let's generate a command for SLURM to launch the program
    ``main.py``.

    >>> from clusterlib.scheduler import submit
    >>> script = submit("python main.py --args 1")
    >>> print(script)
    echo '#!/bin/bash
    python main.py --args 1' | sbatch --job-name=job --time=24:00:00 --mem=4000

    The job can be latter launched using for instance ``os.system(script)``.

    """
    if backend in _TEMPLATE:
        launcher = _LAUNCHER[backend]
        template = _TEMPLATE[backend]
    else:
        raise ValueError("Unknown backend %s expected any of %s"
                         % (backend, "{%s}" % ",".join(_TEMPLATE)))

    job_options = [
        template["job_name"] % job_name,
        template["time"] % time,
        template["memory"] % memory,
    ]

    if email:
        job_options.append(template["email"] % email)

    if email_options:
        job_options.append(template["email_options"] % email_options)

    if log_directory:
        if backend == "sge":
            job_options.append(template["log_directory"] % log_directory)
        elif backend == "slurm":
            job_options.append(template["log_directory"]
                               % (log_directory, job_name))

    # Using echo job_commands | launcher job_options allows to avoid creating
    # a script file. The script is indeed created on the flight.
    command = ("echo '%s\n%s' | %s %s"
               % (shell_script, job_command, launcher, " ".join(job_options)))

    return command
