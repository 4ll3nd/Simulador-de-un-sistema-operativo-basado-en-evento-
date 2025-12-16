class FileSystem():
    def __init__(self):
        self._dict = {}

    def write(self, path, program):
        self._dict[path] = program

    def read(self, path):
        return self._dict[path]