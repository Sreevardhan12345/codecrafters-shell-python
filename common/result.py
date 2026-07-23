class Result:
    def __init__(self, returncode, stdout=None, stderr=None):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr