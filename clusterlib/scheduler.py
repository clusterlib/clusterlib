"""
Module to help working with scheduler such as sun grid engine (SGE) or
Simple Linux Utility for Resource Management (SLURM).

"""

import subprocess
from xml.etree import ElementTree

__all__ = [
    "queued_or_running_jobs",
]

def _sge_queued_or_running_jobs(warn=False):
    try:
        xml = subprocess.check_output("qstat -xml", shell=True,
                                      stderr=subprocess.PIPE)
        tree = ElementTree.fromstring(xml)
        return [leaf.text for leaf in tree.iter("JB_name")]
    except subprocess.CalledProcessError:
        # qstat is not available
        return []


def _slurm_queued_or_running_jobs(warn=False):
    try:
        out = subprocess.check_output("squeue --noheader -o %j", shell=True,
                                      stderr=subprocess.PIPE)
        out = out.split("\n")[:-1]
        return out
    except subprocess.CalledProcessError:
        # squeue is not available
        return []


def queued_or_running_jobs():
    """Return name list of queued or running jobs on SGE and SLURM"""
    return [queued_or_running()
            for queued_or_running in [_sge_queued_or_running_jobs,
                                      _slurm_queued_or_running_jobs]]
