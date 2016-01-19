# Experimental Grid Submission Tool

This is an experimental script that I'm using to submit jobs to the LHC grid.

Using [gevent](http://www.gevent.org/), the Dirac API is converted into an async API that allows you to submit and monitor jobs concurrently.
Although the script runs in a single thread, it submits, monitors and downloads jobs in parallel.

[LevelDB](https://github.com/google/leveldb) is used to persist job information to disk, so that it's not lost between closing and running the script.

## Preparation

Make sure that you have the `gevent` and `leveldb` packages, as well as the Dirac API installed and configured.
Don't forget to initialize a grid proxy:
```
# Example for LHCb
$ lhcb-proxy-init
```

## Submitting jobs

Jobs are defined using the [Dirac Job API](http://diracgrid.org/files/docs/UserGuide/GettingStarted/UserJobs/DiracAPI/index.html) like this:
```python
    j = Job()
    j.setExecutable('echo Hello World')
    j.setName('Test job')
    submit(j)
```
Define your jobs in a Python file and use the implicitly defined `submit` function once they are fully configured.
You can then call
```
python grid.py submit myjobfile.py
```
and the tool will submit the jobs and drop you into the monitoring mode (next section).

## Monitoring jobs

Execute
```
python grid.py watch
```
to monitor changes in job status and download the job output once a job is finished.
The tool will print log messages for status changes, as well as summary lines like
```
S:   0	R:   0	W:   0	M:   0	R:   0	D:  10	F:   0
```
These stand for

| Letter | Meaning |
|--------|---------|
| S      | Submitted |
| R      | Received |
| W      | Waiting | 
| M      | Matched | 
| R      | Running |
| D      | Done | 
| F      | Failed |

The output of 'Done' jobs will be placed in the `succeeded` directory inside the current working directory.
Likewise, you will find the output of failed jobs in `failed`.

### What if I want to run several "batches" of jobs for different purposes?

If you are working on a different task, requiring you to submit a different set of jobs,
simply make a new directory and submit your jobs from there.

## Warnings

Careful, like the Dirac API, this tool does *not* hold your hand at all when it comes to submitting jobs.
It is only recommended for users who absolutely know what they are doing.
Make sure that your configuration is sound and test it before submission.

