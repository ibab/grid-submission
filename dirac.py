#!/usr/bin/env python2
"""Wrap (and simplify) the most used DIRAC commands for easier use."""

from __future__ import print_function

from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb

__all__ = ['DiracException', 'split_input_data']


class DiracException(Exception):
    """Exception in a call to the DIRAC API."""


def bk_query(path, print_stats=False):
    """Query the LHCb Bookeeping for data.

    Print the luminosity associated to the given path.

    Arguments:
        path (str): Path in the Bookkeeping.
        print_stats (bool, optional): Print statistics of
            the files in the requested path. Defaults to False.

    Returns:
        list: LFNs under the requested path.

    """
    resp = DiracLHCb().bkQueryPath(path)
    if not resp['OK']:
        raise DiracException(resp['Message'])
    if print_stats:
        # Available stats:
        # 'Summary': {'EventInputStat': 10195005001,
        #             'FileSize': 2936.24646032,
        #             'InstLuminosity': 0,
        #             'Luminosity': 175061165.465,
        #             'Number Of Files': 1388,
        #             'Number of Events': 33243702,
        #             'TotalLuminosity': 0}}
        lumi = resp['Value']['Summary']['Luminosity'] / 1e9
        num_files = resp['Value']['Summary']['Number Of Files']
        print('Path contains {} files with total luminosity of {} fb^{{-1}}'.format(lumi,
                                                                                    num_files))
    return resp['Value']['LFNs'].keys()


def split_input_data(lfns, max_files_per_job=10):
    """Split LFNs.

    This function wraps `splitInputData` from the DIRAC API.

    Arguments:
        lfns (list): LFNs to split.
        max_files_per_job (int, optional): Maximum files per job.
            Defaults to 10.

    Returns:
        list: Groups of LFNs.

    Raises:
        DiracException: If the call to the API fails.


    """
    res = DiracLHCb().splitInputData(lfns, maxFilesPerJob=max_files_per_job)
    if not res['OK']:
        raise DiracException(res['Message'])
    return res['Value']

# EOF

