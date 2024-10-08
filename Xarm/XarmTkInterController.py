from tkinter import *
from threading import *
from XarmNavigator import XarmNavigator

class XarmTkInterController:

    def __init__(self, navigator):
        self.root = Tk() 
        self.root.geometry("800x800") 

        self.leftframe = Frame(self.root)  
        self.leftframe.pack(side = LEFT)  
        
        self.rightframe = Frame(self.root)  
        self.rightframe.pack(side = RIGHT)
        
        self.robotControl:XarmNavigator = navigator
        
        self.t = None
        self.thr = None    
        
        Button(self.leftframe, text="Baseposition", command=self.basePosition).pack(side = TOP)
        
        Button(self.leftframe, text="Grip open", command=self.gripperOpen).pack(side = TOP)
        Button(self.leftframe, text="Grip close", command=self.gripperClose).pack(side = TOP)
        
        Button(self.leftframe, text="Grap Sphero Camera", command=self.gripBasedOnCameraCenter).pack(side = TOP)
        Button(self.leftframe, text="Drop Sphero Camera", command=self.dropBasedOnCameraCenter).pack(side = TOP)
        
        Button(self.leftframe, text="Grap Sphero", command=self.grip).pack(side = TOP)
        Button(self.leftframe, text="Drop Sphero", command=self.drop).pack(side = TOP)
        
        Button(self.leftframe, text="Start Traject", command=self.traject).pack(side = TOP) 
        Button(self.leftframe, text="Stop traject", command=self.stopThread).pack(side = TOP) 
        
        Button(self.leftframe, text="Move", command=self.move).pack(side = TOP) 
        
        self.createCoordinateInput()
        self.createCoordinateOutput()
        
        self.fillPositionsEntry()
        self.fillPositions()
    
    def gripBasedOnCameraCenter(self):
        self.stopThread()
        self.robotControl.gripBasedOnCameraCenter()
    
    def dropBasedOnCameraCenter(self):
        self.stopThread()
        self.robotControl.dropBasedOnCameraCenter()

    def grip(self):
        self.stopThread()
        self.robotControl.grip()
    
    def drop(self):
        self.stopThread()
        self.robotControl.drop()

    def createCoordinateInput(self):
        self.coordinatesFrame = Frame(self.leftframe)
        self.coordinatesFrame.pack(side = TOP)

        Label(self.coordinatesFrame, text = "x: ").pack(side=LEFT)
        self.xText = StringVar(self.root)
        self.xEntry = Entry(self.coordinatesFrame, textvariable=self.xText, width=3)
        self.xEntry.pack(side =LEFT)
        
        Label(self.coordinatesFrame, text = "y: ").pack(side=LEFT)
        self.yText = StringVar(self.root)
        self.yEntry = Entry(self.coordinatesFrame, textvariable=self.yText, width=3)
        self.yEntry.pack(side =LEFT)
        
        Label(self.coordinatesFrame, text = "z: ").pack(side=LEFT)
        self.zText = StringVar(self.root)
        self.zEntry = Entry(self.coordinatesFrame, textvariable=self.zText, width=3)
        self.zEntry.pack(side =LEFT)
    
    def createCoordinateOutput(self):
        self.coordinatesOutputFrame = Frame(self.leftframe)
        self.coordinatesOutputFrame.pack(side = TOP)

        Label(self.coordinatesOutputFrame, text = "x: ").pack(side=LEFT)
        self.xROText = StringVar(self.root)
        Label(self.coordinatesOutputFrame, textvariable=self.xROText).pack(side=LEFT)
        
        Label(self.coordinatesOutputFrame, text = "y: ").pack(side=LEFT)
        self.yROText = StringVar(self.root)
        Label(self.coordinatesOutputFrame, textvariable=self.yROText).pack(side=LEFT)
        
        Label(self.coordinatesOutputFrame, text = "z: ").pack(side=LEFT)
        self.zROText = StringVar(self.root)
        Label(self.coordinatesOutputFrame, textvariable=self.zROText).pack(side=LEFT)
        
    def fillPositionsEntry(self):
        x, y, z = self.robotControl.getCurrentPos()

        self.xText.set(str(x))
        self.yText.set(str(y))
        self.zText.set(str(z))
        
    def fillPositions(self):
        x, y, z = self.robotControl.getCurrentPos()

        self.xROText.set(str(x))
        self.yROText.set(str(y))
        self.zROText.set(str(z))
    
    def getCoordinateFromGUI(self):
        return (int(self.xText.get()), int(self.yText.get()), int(self.zText.get()))
    
    def run(self):
        self.root.mainloop() 
        
    def basePosition(self):
        self.stopThread()
        self.robotControl.goStart()
        self.fillPositions()
    
    def gripperOpen(self):
        self.stopThread()
        self.robotControl.gripOpen()
        
    def gripperClose(self):
        self.stopThread()
        self.robotControl.gripClose()
    
    def trackSphero(self):
        self.stopThread()
        self.t = Event()
        self.thr = Thread(target = self.robotControl.findSphero, args={self.t,})
        self.thr.start()
    
    def traject(self):
        self.stopThread()
        self.t = Event()
        self.thr = Thread(target = self.robotControl.runTraject, args={self.t,})
        self.thr.start()
    
    def stopThread(self):
        if self.t and self.thr:
            self.t.set()
            self.thr.join()
            self.t = None
            self.thr = None
  
    def move(self): 
        self.robotControl.movePos(self.getCoordinateFromGUI())
