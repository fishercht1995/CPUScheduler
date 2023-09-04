import numpy as np
from . import queue
from .job import Job
from . import analyze
from .utility import generateOutput, checkContextSwitch

class Scheduler:
    def next(self):
        pass

    def enqueue(self, job):
        pass


class RRScheduler(Scheduler):
    def __init__(self):
        self.q = queue.FIFOQueue()

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
class FIFOScheduler(Scheduler):
    def __init__(self):
        self.q = queue.FIFOQueue()

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
class SFSScheduler(Scheduler):
    def __init__(self, timeSlice, period, SRTFSimulationPath = ""):
        self.q = queue.SFSPriorityQueue()
        self.timeSlice = timeSlice
        self.path = SRTFSimulationPath
        self.period = period
        self.orginialTimeSlice = timeSlice
        self.iat = timeSlice
        self.startNum = 0
        self.startT = 0
        self.arrival = 0
        self.waitingT = 0

    def next(self):
        return self.q.dequeue()
    
    def updateArrival(self):
        self.arrival += 1
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def firstEnqueue(self, job):
        self.q.firstEnqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
    def updatePolicy(self, t):
        if self.arrival == 0:
            self.iat = 6
        else:
            # iat
            self.iat = int((t - self.startT)/self.arrival)
            if self.iat < self.orginialTimeSlice:
                self.iat = self.orginialTimeSlice
            self.startT = t
            self.arrival = 0

    def getTimeSlice(self, job):
        if job.Priority == 0:
            lastWaiting = self.waitingT
            self.waitingT = job.waitTime
            if lastWaiting > self.iat:
                return self.iat
            return self.iat
        else:
            return self.orginialTimeSlice

        

    

class SRTFScheduler(Scheduler):
    def __init__(self):
        self.q = queue.SRTFPriorityQueue()

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
    def checkContextSwitch(self, job, timeS):
        if job.executed < timeS:
            return False
        hp_remainingTime = self.q.get_hp_remainingTime()
        if hp_remainingTime:
            return hp_remainingTime < job._remainingTime
        else:
            return False
        
class SEALScheduler(Scheduler):
    def __init__(self, timeSlice, period, SRTFSimulationPath = ""):
        self.q = queue.SEALPriorityQueue()
        self.timeSlice = timeSlice
        self.policies = {i: self.timeSlice for i in range(1,6)}
        self.path = SRTFSimulationPath
        self.period = period
        self.orginialTimeSlice = timeSlice

    def getTimeSlice(self, jb):
        return self.policies[jb.classid]
    
    def updatePolicy(self, log):
        # SRTF simulation
        workload = log.finishedWorkload[-self.period:]
        workload = sorted(workload, key=lambda x: x.startTime)
        tsD, wtD = self.offlineSimulate(workload)
        for classid in tsD:
            tsMedian = np.median(tsD[classid])
            wtMedian = np.median(wtD[classid])
            #print(classid, tsMedian, wtMedian)
            #return time slice - wait time
            self.policies[classid] = int(tsMedian - wtMedian) if tsMedian > wtMedian + 1 else 1
        

    def offlineSimulate(self, workload):
        timePath = {}
        offLog = analyze.simulateLog(self.orginialTimeSlice)
        for jb in workload:
            if jb.startTime not in timePath:
                timePath[jb.startTime] = [jb]
            else:
                timePath[jb.startTime].append[jb]
        offsched = SRTFScheduler()
        t = 0
        finishedJobs = 0
        hasContextSwitch = True
        while finishedJobs < len(workload):
            # start new jobs
            if t in timePath:
                for jb in timePath[t]:
                    offsched.enqueue(jb)      
            # if scheduler queue empty pass
            if offsched.is_empty() and hasContextSwitch:
                t += 1
                offLog.idle += 1
            else:
                if hasContextSwitch:
                    hasContextSwitch = False
                    j = offsched.next()
                    if j.waitTime == -1:
                        j.waitTime = t - j.startTime
                    j.execute()
                    if checkContextSwitch("srtf", j, offsched, self.orginialTimeSlice):
                        # do contextSwitch, if not finished return to the queue
                        hasContextSwitch = True
                        if j.isEnd():
                            finishedJobs += 1
                            j.endTime = t
                            offLog.jobEnd(j, t)
                        else:
                            j.contextS += 1
                            offsched.enqueue(j)
                            offLog.jobContextSwitch(j, t)
                        j.executed = 0
                else:
                    j.execute()
                    hasContextSwitch = False
                    if checkContextSwitch("srtf", j, offsched, self.orginialTimeSlice):
                        # do contextSwitch, if not finished return to the queue
                        hasContextSwitch = True
                        if j.isEnd():
                            finishedJobs += 1
                            j.endTime = t
                            offLog.jobEnd(j, t)
                        else:
                            j.contextS += 1
                            offsched.enqueue(j)
                            offLog.jobContextSwitch(j, t)
                        j.executed = 0
                #if j._remainingTime == 0:
                #print(t, j.name, j._remainingTime, j.executed, len(sched.queue),hasContextSwitch)
                t += 1
        offLog.total = t
   
        tsD = {classid: [] for classid in offLog.trainingData.keys()}
        for classid in offLog.trainingData:
            for timeS in offLog.trainingData[classid]:
                for t in timeS:
                    tsD[classid].append(t)
        wtD = {classid: [] for classid in offLog.jobSummary}
        for classid in offLog.jobSummary:
            for name in offLog.jobSummary[classid]:
                wtD[classid].append(offLog.jobSummary[classid][name]["wait"])
        return tsD, wtD

    def next(self):
        return self.q.dequeue()
    
    def enqueue(self, job):
        self.q.enqueue(job)
    
    def is_empty(self):
        return self.q.is_empty()
    
    def checkContextSwitch(self, job, timeS):
        if job.executed < timeS:
            return False
        hp_priority = self.q.get_hp_priority()
        if hp_priority:
            return hp_priority <= job.Priority
        else:
            return False

