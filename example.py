
for i in range(10):
    j = Job()
    j.setExecutable('echo Hello World')
    j.setName('Test submission script')
    submit(j)

