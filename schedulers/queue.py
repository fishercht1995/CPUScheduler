import heapq

class QueueInterface:
    def enqueue(self, job):
        pass
    
    def dequeue(self, job):
        pass

    def is_empty(self):
        pass

class FIFOQueue(QueueInterface):
    def __init__(self):
        self.queue = []
    
    def enqueue(self, job):
        self.queue.append(job)
    
    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
    

class PriorityQueue(QueueInterface):
    def __init__(self):
        self.queue = []

    def enqueue(self, job):
        heapq.heappush(self.queue, (job.priority, job))
    
    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)[1]
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
