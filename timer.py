import time

class Timer:   
    def __init__(self, name='Timer'):
        self.name = name

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
        print '{0} took time {1}'.format(self.name, self.interval)
