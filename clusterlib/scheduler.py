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
from __future__ import unicode_literals

import os
import subprocess
from xml.etree import ElementTree


__all__ = [
    "queued_or_running_jobs",
    "submit"
]


def _which(program):
    """Check the presence of an executable in the PATH

    Credits: http://stackoverflow.com/questions/377017
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def _get_backend(backend="auto"):
    """Detect the backend to use based on the commands present in the PATH"""
    backend_commands = (
        ('slurm', 'squeue'),
        ('sge', 'qstat'),
    )
    if backend == "auto":
        # If backend is auto, check that it is not configured explicitly
        # in a dedicated environment variable
        backend = os.environ.get('CLUSTERLIB_BACKEND', 'auto').lower()

    if backend == "auto":
        # lookup the command for a suitable backend by order of preference
        for backend_name, backend_cmd in backend_commands:
            if _which(backend_cmd) is not None:
                return backend_name
        raise RuntimeError("Could not find any suitable backend: %s"
                           % ", ".join(b for b, c in backend_commands))

    backend_cmd = dict(backend_commands).get(backend)
    if backend_cmd is None:
        raise ValueError("Unsupported backend: '%s'" % backend)
    return backend


def _sge_queued_or_running_jobs(user=None):
    """Get queued or running jobs from SGE queue system"""
    command = "qstat -xml"
    if user is not None:
        command += " -u {}".format(user)

    try:
        with open(os.devnull, 'w') as shutup:
            xml = subprocess.check_output(command, shell=True, stderr=shutup)
            tree = ElementTree.fromstring(xml)
            return [leaf.text for leaf in tree.iter("JB_name")]
    except subprocess.CalledProcessError:
        # qstat is not available
        return []


def _slurm_queued_or_running_jobs(user=None):
    """Get queued or running jobs from SLURM queue system"""
    command = "squeue --noheader -o %j"
    if user is not None:
        command += " -u {}".format(user)

    try:
        with open(os.devnull, 'w') as shutup:
            out = subprocess.check_output(command, shell=True, stderr=shutup)
            out = out.splitlines()
            return out
    except subprocess.CalledProcessError:
        # squeue is not available
        return []


def queued_or_running_jobs(user=None):
    """Return the names of the queued or running jobs under SGE and SLURM

    The list of jobs could be either the list of all jobs on the scheduler
    or only the jobs associated to the user calling this function.
    The default behavior is dependant upon scheduler configuration.
    Try ``qstat`` in SGE or ``squeue`` in SLURM to know which behavior it
    follows.

    Parameters
    ----------
    user : str or None, (default=None)
        Filter the job list using a given user name.

    Returns
    -------
    out : list of string,
        Returned a list containing all the names of the jobs that are running
        or queued under the SGE or SLURM scheduler.

    """
    out = []
    for queued_or_running in (_sge_queued_or_running_jobs,
                              _slurm_queued_or_running_jobs):
        out.extend(queued_or_running(user=user))

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
           email=None, email_options=None, log_directory=None, backend="auto",
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

    backend : {'auto', 'slurm', 'sge'}, optional (default="auto")
        Backend where the job will be submitted. If 'auto', try detect
        the backend to use based on the commands available in the PATH
        variable.

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
    >>> script = submit("python main.py --args 1", backend='slurm')
    >>> print(script)
    echo '#!/bin/bash
    python main.py --args 1' | sbatch --job-name=job --time=24:00:00 --mem=4000

    The job can be latter launched using for instance ``os.system(script)``.

    """
    backend = _get_backend(backend)
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
