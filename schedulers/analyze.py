import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm

from .job import Job
matplotlib.use('Agg') 

class simulateLog:
    def __init__(self, timeS):
        self.durations = {}
        self.contextS = {}
        self.timeSlice = {}
        self.jobSummary = {}
        self.idle = 0
        self.total = 0
        self.trainingData ={}
        self.finishedWorkload = []
        self.timeS = timeS

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

        if j.classid not in self.trainingData:
            self.trainingData[j.classid] = []
        self.trainingData[j.classid].append(self.timeSlice[j.classid][j.name])

        self.finishedWorkload.append(Job(j.name, j.startTime, j.endTime - j.startTime + 1, j.classid, j.id, j.Priority))
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

def writeLogs(output, durations, contextS, timeS, jobS):
    f = open(output,"w")
    f.write("name; classid; duration; start; burst; end; wait; contextNum; contextSwitch; timeSlice\n")
    for classid in durations:
        for name in durations[classid]:
            duration = durations[classid][name]
            # ContextS
            if name not in contextS[classid]:
                contextSwitch = ""
            else:
                contextD = [str(d) for d in contextS[classid][name]]
                contextSwitch = " ".join(contextD)
            #timeSlice
            if name not in timeS[classid]:
                timeSlice = ""
            else:
                timeSliceD = [str(d) for d in timeS[classid][name]]
                timeSlice = " ".join(timeSliceD)
            #jobSummary
            jobSummaryD = jobS[classid][name]
            f.write("{}; {}; {}; {}; {}; {}; {}; {}; {}; {}\n".format(
                name,
                classid,
                duration,
                jobSummaryD["start"],
                jobSummaryD["burst"],
                jobSummaryD["end"],
                jobSummaryD["wait"],
                jobSummaryD["contextSwitch"],
                contextSwitch,
                timeSlice
            ))
    f.close()

def analyzeData(policies, inputfiles):
    processData = {}
    for i in range(len(policies)):
        processData[policies[i]] = {}
        df = pd.read_csv(inputfiles[i], sep = ";")
        classids = [int(d) for d in list(df[' classid'].unique())]
        for classid in classids:
            subdf = df[df[' classid'] == classid]
            subData = {}
            subData["ContextSwitch"] = int(np.median(subdf[" contextNum"]))
            subData["wait"] = int(np.median(subdf[" wait"]))
            subData["p50"] = int(np.percentile(subdf[" duration"], 50))
            subData["p75"] = int(np.percentile(subdf[" duration"], 75))
            subData["p90"] = int(np.percentile(subdf[" duration"], 90))
            subData["p99"] = int(np.percentile(subdf[" duration"], 99))
            processData[policies[i]][classid] = subData
    return processData

def drawPlot(policies, inputfiles):
    drawCDF(policies, inputfiles)

def drawCDF(policies, inputfiles):
    fig, ax = plt.subplots()
    for i in range(len(policies)):
        p = policies[i]
        durations = sorted(list(pd.read_csv(inputfiles[i], sep = ";")[" duration"]))
        ecdf = sm.distributions.ECDF(durations)
        #等差数列，用于绘制X轴数据
        x = np.linspace(min(durations), max(durations),90000)
        # x轴数据上值对应的累计密度概率
        y = ecdf(x)
        plt.step(x, y,label = p,linewidth=2)
    plt.legend(fontsize = 15)
    plt.xlabel('Durations(ms)',fontsize=25)
    plt.ylabel('CDF',fontsize=25)
    plt.xticks(fontsize= 20)
    plt.yticks(fontsize= 20)
    ax.set_xscale("log")
    plt.tight_layout()
    plt.savefig("./static/cdf.png")
    #plt.show()