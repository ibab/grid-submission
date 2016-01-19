
for i in range(1):
    j = Job()
    j.setExecutable('example_job.sh')
    j.setName('Test submission script')
    j.setInputSandbox(['options.py'])
    submit(j)

