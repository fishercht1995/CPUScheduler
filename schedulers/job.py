class Job:
    def __init__(self, name, startTime, burstTime, classid, Priority = 0):
        self.name = name
        self.startTime = startTime
        self.burstTime = burstTime
        self._remainingTime = self.burstTime
        self.Priority = Priority
        self.classid = classid
        self.executed = 0
        self.endTime = -1
        self.contextS = 0
        self.waitTime = -1
    
    def execute(self):
        self._remainingTime -= 1
        self.executed += 1

    def executedTime(self):
        return self.executed
    
    def isEnd(self):
        return self._remainingTime == 0

