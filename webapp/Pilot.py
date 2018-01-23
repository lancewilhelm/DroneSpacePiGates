class pilot:
    def __init__(self,name="unkown pilot",frequency=5800,color=[175,175,175]):
        self.laps = []
        self.name = name
        self.frequency = frequency
        self.color = color

    def startLap(self):
        if(len(self.laps)>0)):
            start = self.laps[-1].getStartTime()
            newLap = lap(start,start,len(self.laps))
        else:
            newLap = lap(getTime(),None,len(self.laps))
        self.laps.append(newLap)

    def endLap(self):
        self.laps[-1].setEndTime(getTime())
        print(str(self.name)+" completed lap "+str(self.laps-1))

    def getTime(self):
        return int(round(time.time() * 1000))

class lap:
    def __init__(self,start,end,number):
        self.startTime = start
        self.endTime = end
        self.duration = end-start
        self.number = number

    def setEndTime(self,end):
        self.endTime = end
        self.duration = self.endTime-self.start

    def getStartTime(self):
        return self.startTime;
