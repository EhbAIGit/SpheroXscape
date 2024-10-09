from tkinter import *
from threading import *
from XarmNavigator import XarmNavigator
from Constants import *

SIZE_CANVAS_Y = 950
SIZE_CANVAS_X = 950

class XarmTkInterController:

    def __init__(self, navigator):
        self.root = Tk() 
        self.root.title("XarmSpheroControl")
        self.root.geometry("1350x1200") 
        
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self.menu = Menu(self.menubar)
        self.menu.add_command(label="Normal grap", command=self.grip)
        self.menu.add_command(label="Normal drop", command=self.drop)
        self.menu.add_command(label="Grip open", command=self.gripperOpen)
        self.menu.add_command(label="Grip close", command=self.gripperClose)
        self.menu.add_command(label="Drop Sphero Camera", command=self.dropBasedOnCameraCenter)
        
        self.menubar.add_cascade(label="Extra's", menu=self.menu)
        
        #self.root.attributes('-fullscreen', True)

        self.leftframe = Frame(self.root)  
        self.leftframe.pack(side = LEFT)  
        
        self.rightframe = Frame(self.root)  
        self.rightframe.pack(side = RIGHT)
        
        self.robotControl:XarmNavigator = navigator
        
        self.t = None
        self.thr = None    
       
        
        self.belowCanvasFrame = Frame(self.rightframe)
        
        self.prepareCanvas()
        
        Button(self.belowCanvasFrame, text="Start Traject", command=self.traject).pack(side = LEFT) 
        Button(self.belowCanvasFrame, text="Stop traject", command=self.stopThread).pack(side = LEFT) 
        Button(self.belowCanvasFrame, text="Grap Sphero Camera", command=self.gripBasedOnCameraCenter).pack(side = LEFT)
        Button(self.belowCanvasFrame, text="PS 1", command=self.placeSphero1).pack(side = LEFT)
        Button(self.belowCanvasFrame, text="PS 2", command=self.placeSphero2).pack(side = LEFT)
        Button(self.belowCanvasFrame, text="PS 3", command=self.placeSphero3).pack(side = LEFT)
        Button(self.belowCanvasFrame, text="PS 4", command=self.placeSphero4).pack(side = LEFT)
        Button(self.belowCanvasFrame, text="PS 5", command=self.placeSphero5).pack(side = LEFT)
        # Button(self.belowCanvasFrame, text="Grap Sphero from loader", command=self.grapSpheroFromLoader).pack(side = LEFT)
        
        #self.spheroNumberText = StringVar(self.root)
        #self.spheroNumberEntry = Entry(self.belowCanvasFrame, width=3, textvariable=self.spheroNumberText)
        #self.spheroNumberEntry.pack(side = LEFT)
        #Button(self.belowCanvasFrame, text="Grap all Sphero's", command=self.placeAllSpheros).pack(side = LEFT)
        
        self.belowCanvasFrame.pack(side = BOTTOM)
        
        
        
    def prepareCanvas(self):
        
        self.createCoordinateInput()
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
    
    def drawLinesOnCanvas(self, coords):
        for pos in range(1, len(coords)):
            startX, startY = self.xarmToCanvasCoord(coords[pos - 1])
            endX, endY = self.xarmToCanvasCoord(coords[pos])
            self.canvas.create_line(startX, startY, endX, endY)

    def canvasCallback(self, event):
        print("clicked at", event.x, event.y)
        coord = (event.x, event.y)
        self.drawCanvas(coord)
        x, y = self.canvasToXarmCoord(coord)
        self.xText.set(str(x))
        self.yText.set(str(y))

    def placeSphero1(self):
        self.robotControl.dropLoadPos(1)

    def placeSphero2(self):
        self.robotControl.dropLoadPos(2)
        
    def placeSphero3(self):
        self.robotControl.dropLoadPos(3)

    def placeSphero4(self):
        self.robotControl.dropLoadPos(4)
    
    def placeSphero5(self):
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

    def createCoordinateInput(self):
        self.coordinatesFrame = Frame(self.rightframe)
        self.coordinatesFrame.pack(side = TOP)

        Button(self.coordinatesFrame, text="Go baseposition", command=self.basePosition).pack(side = LEFT)

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

    """    
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
    """
        
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
        self.robotControl.movePosWithTour(self.getCoordinateFromGUI())
