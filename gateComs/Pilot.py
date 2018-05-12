import time
class pilot:
    def __init__(self,name="unkown pilot",frequency=5800,animation="bluebang",color=[0.33,0.33,0.33]):
        self.laps = []
        self.name = name
        self.frequency = frequency
        self.animation = animation
        self.readyForLap = True
        self.distance = 100
        self.color = color

    def addLap(self,start,end):
        newLap = lap(start,end,len(self.laps))
        self.laps.append(newLap)

    def getCurrentLapDuration(self):
        duration = 0
        if(len(self.laps)>0):
            duration = self.laps[-1].getDuration()
        return duration

    def getTime(self):
        return int(round(time.time() * 1000))

    def getAnimation(self):
        return self.animation

class lap:
    def __init__(self,start,end,number):
        self.startTime = start
        self.endTime = end
        self.duration = end-start
        self.number = number

    def getTime(self):
        return int(round(time.time() * 1000))

    def setEndTime(self,end):
        self.endTime = end
        self.duration = self.endTime-self.startTime

    def getDuration(self):
        self.duration = self.getTime()-self.startTime
        return self.duration

    def getStartTime(self):
        return self.startTime;
