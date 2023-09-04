from . import scheduler
from . import job
from . import analyze
class simulateLog:
    def __init__(self):
        self.durations = {}
        self.contextS = {}
        self.timeSlice = {}
        self.jobSummary = {}
        self.idle = 0
        self.total = 0
    def jobEnd(self, j, t):
        # update durations
        if j.classid not in self.durations:
            self.durations[j.classid] = {}
        self.durations[j.classid][j.name] = j.endTime - j.startTime

        # update jobSummary
        if j.classid not in self.jobSummary:
            self.jobSummary[j.classid] = {}
        self.jobSummary[j.classid][j.name] = {"start": j.startTime, "burst": j.burstTime, "end": j.endTime, "wait": j.waitTime, "contextSwitch": j.contextS}

        self.jobContextSwitch(j, t)
    def jobContextSwitch(self,j,t):
        # update contextS
        if j.classid not in self.contextS:
            self.contextS[j.classid] = {}
        if j.name not in self.contextS[j.classid]:
            self.contextS[j.classid][j.name] = []
        self.contextS[j.classid][j.name].append(t)

        # update timeslice
        if j.classid not in self.timeSlice:
            self.timeSlice[j.classid] = {}
        if j.name not in self.timeSlice[j.classid]:
            self.timeSlice[j.classid][j.name] = []
        self.timeSlice[j.classid][j.name].append(j.executed)
    
def generateOutput(slog, outPath):
    # write data
    analyze.writeLogs(outPath, slog.durations, slog.contextS, slog.timeSlice, slog.jobSummary)

def checkContextSwitch(policy, j, sched, timeSlice):
    if policy in ["fifo", "rr"]:
        return (j.executedTime() >= timeSlice and not sched.is_empty()) or j.isEnd()
    else:
        return False

def simulate(workloads, policy, outpath, timeSlice = 6):
    # build workload time path
    timePath = {}
    log = simulateLog()
    for jb in workloads:
        if jb.startTime not in timePath:
            timePath[jb.startTime] = [jb]
        else:
            timePath[jb.startTime].append(jb)

    # initialize scheduler
    if policy == "fifo":
        timeSlice = 9999
        sched = scheduler.FIFOScheduler()
    elif policy == "rr":
        sched = scheduler.RRScheduler()
    t = 0
    finishedJobs = 0
    hasContextSwitch = True
    while finishedJobs < len(workloads):
        # start new jobs
        if t in timePath:
            for jb in timePath[t]:
                sched.enqueue(jb)
        
        # if scheduler queue empty pass
        if sched.is_empty() and hasContextSwitch:
            t += 1
            log.idle += 1
        else:
            if hasContextSwitch:
                hasContextSwitch = False
                j = sched.next()
                if j.waitTime == -1:
                    j.waitTime = t - j.startTime
                j.execute()
                if checkContextSwitch(policy, j, sched, timeSlice):
                    # do contextSwitch, if not finished return to the queue
                    hasContextSwitch = True
                    if j.isEnd():
                        finishedJobs += 1
                        j.endTime = t
                        log.jobEnd(j, t)
                    else:
                        j.contextS += 1
                        sched.enqueue(j)
                        log.jobContextSwitch(j, t)
                    j.executed = 0
            else:
                j.execute()
                hasContextSwitch = False
                if checkContextSwitch(policy, j, sched, timeSlice):
                    # do contextSwitch, if not finished return to the queue
                    hasContextSwitch = True
                    if j.isEnd():
                        finishedJobs += 1
                        j.endTime = t
                        log.jobEnd(j, t)
                    else:
                        j.contextS += 1
                        sched.enqueue(j)
                        log.jobContextSwitch(j, t)
                    j.executed = 0
            #if j._remainingTime == 0:
            #print(t, j.name, j._remainingTime, j.executed, len(sched.queue),hasContextSwitch)
            t += 1
    log.total = t
    generateOutput(log, outpath+"data.csv")
    #print(log.contextS)
    #print(log.durations)
    #print(log.timeSlice)
    #print(log.jobSummary)
    print(1 - log.idle/log.total)

def test():
    a = job.Job("fib1", 0, 100)
    b = job.Job("fib2", 1, 10)
    c = job.Job("fib3", 15, 20)
    workloads = [a,b,c]
    a = {"cfs":{1:{50:30, 75: 40}, 2:{50:30, 75: 40}}, "fifo":{1:{50:30, 75: 40}, 2:{50:30, 75: 40}}}
    simulate(workloads, "fifo")