from . import scheduler
from . import job
from . import analyze
from .utility import generateOutput, checkContextSwitch


def simulate(workloads, policy, outpath, timeSlice = 6, period = 1000, CScost = 1):
    # build workload time path
    timePath = {}
    log = analyze.simulateLog(timeSlice)
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
    elif policy == "srtf":
        sched = scheduler.SRTFScheduler()
    elif policy == "seal":
        sched = scheduler.SEALScheduler(timeSlice, period)
    elif policy == "sfs":
        sched = scheduler.SFSScheduler(timeSlice, period)
    t = 0
    finishedJobs = 0
    hasContextSwitch = True
    started = 0
    CScostSignal = False
    while finishedJobs < len(workloads):
        # start new jobs
        if t in timePath:
            for jb in timePath[t]:
                if policy == "sfs":
                    jb.Priority = 0
                    sched.updateArrival()
                    sched.firstEnqueue(jb)
                    if started % period == 0 and policy == "sfs":
                        sched.updatePolicy(t)
                else:
                    sched.enqueue(jb)
                started += 1
        if CScostSignal:
            t += CScost
            CScostSignal = False
            continue
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
                if policy == "seal":
                    timeSlice = sched.getTimeSlice(j)
                elif policy == "sfs":
                    timeSlice = sched.getTimeSlice(j)
                    j.Priority = 99
                j.execute()
                if checkContextSwitch(policy, j, sched, timeSlice):
                    # do contextSwitch, if not finished return to the queue
                    CScostSignal = True
                    hasContextSwitch = True
                    if j.isEnd():
                        finishedJobs += 1
                        j.endTime = t
                        log.jobEnd(j, t)
                        if finishedJobs % period == 0 and policy == "seal":
                            sched.updatePolicy(log)
                        if started % period == 0 and policy == "sfs":
                            sched.updatePolicy(t)
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
                    CScostSignal = True
                    hasContextSwitch = True
                    if j.isEnd():
                        finishedJobs += 1
                        j.endTime = t
                        log.jobEnd(j, t)
                        if finishedJobs % period == 0 and policy == "seal":
                            sched.updatePolicy(log)
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