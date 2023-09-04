from . import job

def readWorkload(inPath):
    lines = open(inPath,"r").readlines()
    w = []
    for line in lines:
        invocationId, startTime, burstTime, class_id, jobid = line.strip().split()
        w.append(job.Job(invocationId, int(startTime), int(burstTime), int(class_id), int(jobid), int(class_id)))
    return w