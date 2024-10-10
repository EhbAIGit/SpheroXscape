from Boundaries import SquareBoundary, LineBoundary
from Constants import *
from XarmUPath import XarmUPath, PathDirection
from XarmSpheroEvents import XarmSpheroEvents
import threading
import time

class XarmNavigator:
    def __init__(self, driver, spheroDetectorFactory, events = XarmSpheroEvents()):
        self.driver = driver
        self.spheroDetectorFactory = spheroDetectorFactory
        
        self.zMin = Z_MIN
        self.zMax = Z_MAX
        
        self.outerBoundary = OUTER_BOUNDARY
        self.innerBoundary = INNER_BOUNDARY
        self.lineBoundary  = BACK_BOUNDARY
               
        self.path = XarmUPath(START_POS, SCAN_NEXT_Y, SCAN_NEXT_X)
        self.events = events
        
        self.x, self.y, self.z = self.driver.getLivePosition()
        self.goStart()
        self.events.applicationStarted(self.getCurrentPos())
        
    def goStart(self):
        self.movePosWithTour(START_POS)
        
    def grip(self, newZ=220):
        x, y, z = self.getCurrentPos()
        self.movePos((x, y, newZ))
        self.gripClose()
        time.sleep(2)
        self.movePos((x, y, z))
        self.events.spheroCatched((x, y, newZ))
    
    def drop(self, newZ=220):
        x, y, z = self.getCurrentPos()
        self.movePos((x, y, newZ))
        self.gripOpen()
        time.sleep(2)
        self.movePos((x, y, z))
        self.events.spheroDroppedAt((x, y, newZ))
    
    def gripBasedOnCameraCenter(self):
        x, y, z = self.getCurrentPos()
        catchPosition = (x + 58, y + 20 ,220)
        self.movePos(catchPosition)
        self.gripClose()
        time.sleep(2)
        self.movePos((x, y, z))
        self.events.spheroCatched(catchPosition)
    
    def dropBasedOnCameraCenter(self):
        x, y, z = self.getCurrentPos()
        dropPosition = (x + 58, y + 20 ,220)
        self.movePos(dropPosition)
        self.gripOpen()
        time.sleep(2)
        self.movePos((x, y, z))
    
    def checkPos(self, x, y, z):
        isOk = self.outerBoundary.inside((x, y)) \
           and self.innerBoundary.trajectDoesntCross((self.x, self.y), (x, y)) \
           and self.lineBoundary.trajectDoesntCross((self.x, self.y), (x, y)) \
           and self.zMin <= z <= self.zMax
        
        if (not isOk):
            print(f"Beweging {(self.x, self.y, self.z)} naar {(x,y,z)} is niet toegelaten")
        
        return isOk
    
    def gripAllLoadPos(self):
        self.events.gettingSpherosFromLoadstation(self.getCurrentPos())
        for i in range(len(LOAD_POSITIONS)):
            self.gripLoadPos(i + 1)
    
    def gripLoadPos(self, loadNumber):
        if(loadNumber > 0 and loadNumber <= len(LOAD_POSITIONS)):
            self.movePosWithTour(LOAD_POSITIONS[loadNumber - 1])
            self.grip(LOAD_GRIP_Z)
            self.movePosWithTour(DROP_POSITIONS[loadNumber - 1])
            self.drop()
    
    def dropLoadPos(self, loadNumber):
        if(loadNumber > 0 and loadNumber <= len(LOAD_POSITIONS)):
            self.movePosWithTour(LOAD_POSITIONS[loadNumber - 1])
            self.drop(LOAD_GRIP_Z)
            self.movePosWithTour(DROP_POSITIONS[loadNumber - 1])
            self.events.spheroDroppedAtLoader(self.getCurrentPos(), loadNumber)
 
    def getCurrentPos(self):
        return (self.x, self.y, self.z)
    
    def moveXForward(self, units):
        self.goX(self.x + units)

    def moveXBackward(self, units):
        self.moveXForward(-units)
    
    def moveYForward(self, units):
        self.goY(self.y + units)

    def moveYBackward(self, units):
        self.moveYForward(-units)

    def moveZForward(self, units):
        self.goZ(self.z + units)

    def moveZBackward(self, units):
        self.moveZForward(-units)
        
    def moveXY(self, x, y):
        self.movePos((self.x + x, self.y + y, self.z))

    def goX(self, newX):
        return self.movePos((newX, self.y, self.z))
    
    def goY(self, newY):
        return self.movePos((self.x, newY, self.z))

    def goZ(self, newZ):
        return self.movePos((self.x, self.y, newZ))
        
    def moveTraject(self, traject):
        for coordinates in traject :
            if not self.movePos(coordinates):
                return
    
    def isAllowedPosition(self,x,y):
        return self.outerBoundary.inside((x, y)) and self.innerBoundary.outside((x, y))
    
    def movePos(self, coordinate):
        x, y, z = coordinate
        if self.checkPos(x, y, z):
            self.driver.initPos(coordinate)
            self.x = x
            self.y = y
            self.z = z
            return True
        else:
            return False
        
    def movePosWithTour(self, coordinate):
        x, y, z = coordinate
        if self.checkPos(x, y, z):
            self.driver.initPos(coordinate)
            self.x = x
            self.y = y
            self.z = z
            return True
        else:
            if self.isAllowedPosition(x, y):
                points = self.path.drawPath(self.getCurrentPos(), coordinate)
                for point in points:
                    self.movePos(point)
                                
                return True
            
            return False
           
    def moveToClosestSphero(self):
        spheroDetector = self.spheroDetectorFactory.getSpheroDetector()
        if spheroDetector:
            time.sleep(0.25)
            coordinates = spheroDetector.detectCircle()
            if coordinates:
                _, _, deltaX, deltaY = coordinates[0]
                self.movePos(((self.x + deltaX), (self.y + deltaY), self.z))
 
    def isInfBoundsForDetection(self, c):
        _, _, deltaX, deltaY = c
        newPosition = ((self.x + deltaX), (self.y + deltaY), self.z)
        return newPosition[1] < Y_DETECTION_BOUNDARY_FOR_LOAD
 
    def recover(self):
        self.driver.recover()
 
    def trackSphero(self, event: threading.Event, maxSeconds = None):
        spheroDetector = self.spheroDetectorFactory.getSpheroDetector()
        if spheroDetector:
            time.sleep(WARMUP_CAM)
            lastTime = time.time()
            while True:
                if event.isSet():
                    return
                
                newTime = time.time()
                if maxSeconds:
                    if newTime > lastTime + maxSeconds:
                        return
                
                coordinates = spheroDetector.detectCircle()
                if coordinates:
                    allowedCoordinates = list(filter(self.isInfBoundsForDetection, coordinates))
                    if allowedCoordinates:
                        lastTime = time.time()
                        _, _, deltaX, deltaY = allowedCoordinates[0]
                        self.movePos(((self.x + deltaX), (self.y + deltaY), self.z))

    def findSphero(self, event: threading.Event, maxTimes=20):
        spheroDetector = self.spheroDetectorFactory.getSpheroDetector()
        if spheroDetector:
            time.sleep(WARMUP_CAM)
            for i in range(maxTimes):
                if event.isSet():
                    return
                
                coordinates = spheroDetector.detectCircle()
                if coordinates:
                    allowedCoordinates = list(filter(self.isInfBoundsForDetection, coordinates))
                    if allowedCoordinates:
                        return True
        return False
    
    def runTraject(self, event: threading.Event):
        lastDirection = PathDirection.RIGHT
        self.events.trajectStarted(self.getCurrentPos())
        
        while True:
            if event.isSet():
                self.events.trajectStopped(self.getCurrentPos())
                return
            
            time.sleep(0.5)
            
            res, xn = self.moveYAndScanN(event, lastDirection)
            lastDirection = xn.direction
            
            if res:
                print("found 1")
                self.trackSphero(event, WAIT_TIME_BEFORE_STOP_TRACKING)
                self.events.spheroLost(self.getCurrentPos)
    
    def moveYAndScanN(self, event, direction):        
        xn = self.path.startCloseTo(self.getCurrentPos(), direction)         
        while(True):
            if event.isSet():
                return (False, xn)
            self.movePos(xn.next())
            if self.findSphero(event):
                self.events.spheroDetected(self.getCurrentPos())
                return (True, xn)
    
    def trackSpheroY(self, xPos):
        spheroDetector = self.spheroDetectorFactory.getSpheroDetector()
        if spheroDetector:
            time.sleep(1)
            while True:
                time.sleep(0.5)
                coordinates = spheroDetector.detectCircle()
                print(coordinates)
                if coordinates:
                    _, _, deltaX, deltaY = coordinates
                    self.movePos((xPos, (self.y + deltaY), self.z))
    

    def gripOpen(self):
        self.driver.gripOpen()
        return 0

    def gripClose(self):
        self.driver.gripClose()
        return 0

    def stateIsOk(self):
        return self.driver.stateIsOk()    

    def release(self):
        self.driver.release()    