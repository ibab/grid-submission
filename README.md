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

## How do I run LHCb software?

Create a script (e.g. `job.sh`) and initialize the LHCb software like this:
```bash
#!/bin/sh

source /cvmfs/lhcb.cern.ch/lib/LbLogin.sh
lb-run DaVinci v38r0 gaudirun.py options.py
```
You can then run your script as part of the job
```python
j = Job()
j.setExecutable('job.sh')
j.setInputSandbox(['options.py'])
```
Don't forget to put the options file in your input sandbox (as above).

## How do I run customized LHCb software?

If you're using CMake to compile your software and you have a Dev directory like `DaVinciDev_v38r0`,
make sure to compile your software, and then zip up the Dev directory and all your inputs like this:

```bash
zip -r job.zip DaVinciDev_v38r0 options.py
```

In your `job.sh`, you have to unzip the directory and simply use the `run` script in the Dev directory like this:
```bash
#!/bin/sh

source /cvmfs/lhcb.cern.ch/lib/LbLogin.sh

unzip job.zip

DaVinciDev_v38r0/run gaudirun.py options.py
```

You can declare the `job.zip` as part of your input sandbox:
```python
j.setInputSandbox(['job.zip'])
```

If you want to submit your jobs faster, or if the input sandbox would be quite large, it can make sense to upload the `job.zip`
to EOS and download it from your grid job using `xrdcp`.

## How do I customize my options per job?

You can pass command line arguments to the `job.sh` and add additional configuration inside `job.sh` like this:
```bash
echo "DaVinci().EvtMax = $1" >> options.py
```
Here `$1` is the first argument passed to `job.sh`.
Your `job.py` could look like this:
```python
for i in range(100):
    evt_max = compute_evt_max(i)
    j = Job()
    j.setExecutable('job.sh {}'.format(evt_max))
    j.setName('Job {}'.format(i))
    submit(j)
```

## How do I access files registered in the LHCb Bookkeeping?

A `bkQuery` function is defined inside your job script.
When passed a bookkeeping path, it will return all LFNs for that path.

Example:
```python
lfns = bkQuery("/LHCb/Collision15/Beam6500GeV-VeloClosed-MagDown/Real Data/Reco15a/Stripping23r1/90000000/CHARMCOMPLETEEVENT.DST")
```

Feel free to access the LHCbDirac API directly inside your job script if you need more flexibility:
```python
from LHCbDIRAC.Interfaces.API.DiracLHCb import DiracLHCb
diracLHCb = DiracLHCb()
resp = diracLHCb.bkQueryPath(path)
lfns = resp['Values']['LFNs'].keys()
```

## How do I split my jobs by LFNs?

Dirac allows you to split your input files into groups of a desired maximum size,
where each group only contains LFNs from a certain storage element.

Use the Dirac API:
```python
groups = dirac.splitInputData(lfns, maxFilesPerJob=10)['Values']
```
`groups` is now a list of lists containing the LFNs.
In order to set these, you can use
```python
for group in groups:
    j = Job()
    ...
    j.setInputData(group)
    ...
    submit(j)
```
Careful: You have to make sure that the right LFNs are used by DaVinci as well.
For example, you could write them to a Python file that is different per job.

