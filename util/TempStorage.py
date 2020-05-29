import os, uuid

class TempFile:
    def __init__(self, directory):
        self.filename = os.path.join(directory, uuid.uuid4().hex)
        self.f = open(self.filename, 'w+b')

    def __del__(self):
        self.f.close()
        os.remove(self.filename)

    def get(self):
        return self.f

    def read(self):
        self.f.seek(0)
        return self.f.read()