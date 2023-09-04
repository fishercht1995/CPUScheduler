from . import queue

class Scheduler:
    def next(self):
        pass

    def enqueue(self, job):
        pass


class RRScheduler(Scheduler):
    def __init__(self):
        self.queue = queue.FIFOQueue()

    def next(self):
        return self.queue.dequeue()
    
    def enqueue(self, job):
        self.queue.enqueue(job)
    
    def is_empty(self):
        return self.queue.is_empty()
    
class FIFOScheduler(Scheduler):
    def __init__(self):
        self.queue = queue.FIFOQueue()

    def next(self):
        return self.queue.dequeue()
    
    def enqueue(self, job):
        self.queue.enqueue(job)
    
    def is_empty(self):
        return self.queue.is_empty()
    

