import os
import random
import pandas as pd
import numpy as np

INVOCATION_PATTERN = {1: 40.6, 2:9.8, 3: 6.8, 4: 22.7, 5: 15.7}
JOB_DURATIONS = {1: 25, 2: 75, 3: 150, 4: 300, 5: 2000}
def readPattern(traceFile = "trace/invocations_per_function_md.anon.d01.csv", t = 0):
    pass

def generateJob(std):
    classid = random.choices(list(INVOCATION_PATTERN.keys()), weights=list(INVOCATION_PATTERN.values()))[0]
    burstTime = int(JOB_DURATIONS[classid] + np.random.normal(0, std * JOB_DURATIONS[classid]))
    if burstTime < 10:
        burstTime = 10
    functype = "function" + str(classid)
    return functype, burstTime, classid

def generateWorkload(N, iat, outPath, std):
    totalTime = N*iat
    timeList = sorted(random.sample(range(totalTime), N))
    f = open(outPath, 'w')
    i = 0
    for t in timeList:
        functype, burstTime, class_id = generateJob(std)
        invocationId = "{}_{}".format(functype, i)
        startTime = t
        i += 1
        f.write("{} {} {} {} {}\n".format(invocationId, startTime, burstTime, class_id, i))
    f.close()


