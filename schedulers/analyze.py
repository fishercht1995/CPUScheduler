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

def writeDurations(d, output):
    f = open(output,"w")
    for classid in d:
        for name in d[classid]:
            f.write("{};{};{}\n".format(classid, name, d[classid][name]))
    f.close()

def writeContextS(d, output):
    f = open(output, "w")
    for classid in d:
        for name in d[classid]:
            f.write("{};{};{}\n".format(classid, name, " ".join(d[classid][name])))
    f.close()

def writeTimeSlice(d, output):
    f = open(output, "w")
    for classid in d:
        for name in d[classid]:
            f.write("{};{};{}\n".format(classid, name, " ".join(d[classid][name])))
    f.close()