from tkinter import *
from threading import *
from XarmNavigator import XarmNavigator
from Constants import *

SIZE_CANVAS_Y = 930
SIZE_CANVAS_X = 930

class XarmTkInterController:

    def __init__(self, navigator):
        self.root = Tk() 
        self.root.title("XarmSpheroControl")
        self.root.geometry("1100x1200") 
        
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self.menu = Menu(self.menubar)
        self.menu.add_command(label="Normal grap", command=self.grip)
        self.menu.add_command(label="Normal drop", command=self.drop)
        self.menu.add_command(label="Grip open", command=self.gripperOpen)
        self.menu.add_command(label="Grip close", command=self.gripperClose)
        self.menu.add_command(label="Drop Sphero Camera", command=self.dropBasedOnCameraCenter)
        self.menu.add_command(label="Reset", command=self.reset)
        
        self.menubar.add_cascade(label="Extra's", menu=self.menu)
        
       
        self.rightframe = Frame(self.root)  
        self.rightframe.pack(side = RIGHT)
        
        self.robotControl:XarmNavigator = navigator
        
        self.t = None
        self.thr = None    
       
        self.belowCanvasFrame = Frame(self.rightframe)
        
        Button(self.belowCanvasFrame, text="Place all Sphero's", command=self.placeAllSpheros).grid(row=0, sticky="EW") 
        
        self.placeAndDropButtons = Frame(self.belowCanvasFrame)
        
        Button(self.placeAndDropButtons, text="GS 1", command=self.gripSphero1).grid(column=0, row=0, sticky="EW")
        Button(self.placeAndDropButtons, text="GS 2", command=self.gripSphero2).grid(column=1, row=0, sticky="EW")
        Button(self.placeAndDropButtons, text="GS 3", command=self.gripSphero3).grid(column=2, row=0, sticky="EW")
        Button(self.placeAndDropButtons, text="GS 4", command=self.gripSphero4).grid(column=3, row=0, sticky="EW")
        Button(self.placeAndDropButtons, text="GS 5", command=self.gripSphero5).grid(column=4, row=0, sticky="EW")
        
        Button(self.placeAndDropButtons, text="DS 1", command=self.dropSphero1).grid(column=0, row=1, sticky="EW")
        Button(self.placeAndDropButtons, text="DS 2", command=self.dropSphero2).grid(column=1, row=1, sticky="EW")
        Button(self.placeAndDropButtons, text="DS 3", command=self.dropSphero3).grid(column=2, row=1, sticky="EW")
        Button(self.placeAndDropButtons, text="DS 4", command=self.dropSphero4).grid(column=3, row=1, sticky="EW")
        Button(self.placeAndDropButtons, text="DS 5", command=self.dropSphero5).grid(column=4, row=1, sticky="EW")
        
        self.placeAndDropButtons.grid(row=1, sticky="EW")
        
        self.trajectFrame = Frame(self.belowCanvasFrame)
        Button(self.trajectFrame, text="Start Traject", command=self.traject).grid(row=0, column=0, sticky="EW")
        Button(self.trajectFrame, text="Stop traject", command=self.stopThread).grid(row=0, column=1,  sticky="EW")
        self.trajectFrame.grid(row=2, sticky="EW", pady=10)
        
        Button(self.belowCanvasFrame, text="Grap Sphero Camera", command=self.gripBasedOnCameraCenter).grid(row=3, sticky="EW")
        
        self.belowCanvasFrame.pack(side = LEFT)
        
        self.createCoordinateInput()
        
        self.prepareCanvas()

    def createCoordinateInput(self):
        self.coordinatesFrame = Frame(self.belowCanvasFrame)
        self.coordinatesFrame.grid(row=5, sticky="EW", pady=10)

        Button(self.coordinatesFrame, text="Base", command=self.basePosition).pack(side = LEFT)

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
        
        Button(self.coordinatesFrame, text="Move", command=self.move).pack(side = LEFT)
    
    def prepareCanvas(self):
        self.fillPositionsEntry()
        
        self.canvas = Canvas(self.rightframe, bg="white", height=950, width=950)
        self.canvas.bind("<Button-1>", self.canvasCallback)
        
        self.drawCanvas()
        
        self.canvas.pack()
    
    def drawCanvas(self, point = None):
        self.canvas.delete("all")
        self.drawLinesOnCanvas(INNER_BOUNDARY.coords)
        self.drawLinesOnCanvas(OUTER_BOUNDARY.coords)
        self.drawLinesOnCanvas(BACK_BOUNDARY.coords)
        if point:
            self.drawPointOnCanvas(point)
    
    def xarmToCanvasX(self, x):
        return (SIZE_CANVAS_X // 2) - x
    
    def xarmToCanvasY(self, y):
        return (SIZE_CANVAS_Y // 2) - y
        
    def xarmToCanvasCoord(self, coord):
        x, y = coord
        return (self.xarmToCanvasX(x), self.xarmToCanvasY(y))

    def canvasToXarmX(self, x):
        return (SIZE_CANVAS_X // 2) - x
    
    def canvasToXarmY(self, y):
        return (SIZE_CANVAS_Y // 2) - y
        
    def canvasToXarmCoord(self, coord):
        x, y = coord
        return (self.canvasToXarmX(x), self.canvasToXarmY(y))

    def drawPointOnCanvas(self, point):
        x, y = point
        x1, y1 = (x - 1), (y - 1)
        x2, y2 = (x + 1), (y + 1)
        dotColor = "#476042"
        self.canvas.create_oval(x1, y1, x2, y2, fill=dotColor, outline=dotColor, width=10)
    
    def invertY(self, y):
        return SIZE_CANVAS_Y - y
    
    def drawLinesOnCanvas(self, coords):
        for pos in range(1, len(coords)):
            startX, startY = self.xarmToCanvasCoord(coords[pos - 1])
            endX, endY = self.xarmToCanvasCoord(coords[pos])
            self.canvas.create_line(startX, self.invertY(startY), endX, self.invertY(endY))

    def canvasCallback(self, event):
        coord = (event.x, event.y)
        self.drawCanvas(coord)
        x, y = self.canvasToXarmCoord(coord)
        self.xText.set(str(x))
        self.yText.set(str(-y))
    
    def reset(self):
        self.robotControl.recover()

    def gripSphero1(self):
        self.robotControl.gripLoadPos(1)

    def gripSphero2(self):
        self.robotControl.gripLoadPos(2)
        
    def gripSphero3(self):
        self.robotControl.gripLoadPos(3)

    def gripSphero4(self):
        self.robotControl.gripLoadPos(4)
    
    def gripSphero5(self):
        self.robotControl.gripLoadPos(5)
    
    def dropSphero1(self):
        self.robotControl.dropLoadPos(1)

    def dropSphero2(self):
        self.robotControl.dropLoadPos(2)
        
    def dropSphero3(self):
        self.robotControl.dropLoadPos(3)

    def dropSphero4(self):
        self.robotControl.dropLoadPos(4)
    
    def dropSphero5(self):
        self.robotControl.dropLoadPos(5)
    
    def placeSphero(self):
        nr = int(self.spheroNumberText.get())
        self.robotControl.dropLoadPos(nr)

    def grapSpheroFromLoader(self):
        pass
    
    def placeAllSpheros(self):
        self.stopThread()
        self.robotControl.gripAllLoadPos()
    
    def gripBasedOnCameraCenter(self):
        self.stopThread()
        self.robotControl.gripBasedOnCameraCenter()
    
    #TODO block during session and provide reset button
    def dropBasedOnCameraCenter(self):
        self.stopThread()
        self.robotControl.dropBasedOnCameraCenter()

    def grip(self):
        self.stopThread()
        self.robotControl.grip()
    
    def drop(self):
        self.stopThread()
        self.robotControl.drop()

    def fillPositionsEntry(self):
        x, y, z = self.robotControl.getCurrentPos()

        self.xText.set(str(x))
        self.yText.set(str(y))
        self.zText.set(str(z))
        
    def getCoordinateFromGUI(self):
        return (int(self.xText.get()), int(self.yText.get()), int(self.zText.get()))
    
    def run(self):
        self.root.mainloop() 
        
    def basePosition(self):
        self.stopThread()
        self.robotControl.goStart()
        x,y,_ = self.robotControl.getCurrentPos()
        self.drawCanvas((self.xarmToCanvasX(x), self.xarmToCanvasY(y)))
        self.fillPositionsEntry()
    
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
        self.stopThread()
        self.robotControl.movePosWithTour(self.getCoordinateFromGUI())
