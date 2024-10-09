import math
from Coordinates import minY, minX, addY, dim2
from enum import Enum

class PathDirection(Enum):
    LEFT = 1
    RIGHT = 2

class XarmUPath:
    def __init__(self,middle, dy, dx):
        self.middle = middle
        self.dy = dy
        self.dx = dx
        
        self.track = []
        self._addLeftSide()
        self.track.append(self.middle)
        self._addRightSide()
 
    def _addLeftSide(self):
        next = self.middle   
        
        for _ in range(2):
            next = minY(next, self.dy)
            self.track.append(next)
    
        for _ in range(4):
            next = minX(next, self.dx)
            self.track.append(next)
        self.track.reverse()
    
    def _addRightSide(self):
        next = self.middle
        for _ in range(2):
            next = addY(next, self.dy)
            self.track.append(next)
    
        for _ in range(4):
            next = minX(next, self.dx)
            self.track.append(next)
        
        for _ in range(1):
            next = minY(next, self.dy)
            self.track.append(next)
    
    def getClosestTo(self, coordinate):
        return sorted(self.track, key = lambda x: math.dist(dim2(x),dim2(coordinate)))
    
    def getClosestPointTo(self, coordinate):
        return self.getClosestTo(coordinate)[0]
    
    def drawPath(self, start, destination):
        closestPointToStart = self.getClosestPointTo(start)
        closestPointToTarget = self.getClosestPointTo(destination)
        
        startIndex = self.track.index(closestPointToStart)
        destinationIndex = self.track.index(closestPointToTarget)
        
        result = []
        
        if startIndex < destinationIndex:
            for i in range(startIndex, destinationIndex + 1):
                result.append(self.track[i])
        else:
            for i in range(startIndex, destinationIndex - 1, -1):
                result.append(self.track[i])
        
        result.append(destination)
        return result
        
            
    def startCloseTo(self, coordinate, direction = PathDirection.RIGHT):
        startPos = self.track.index(self.getClosestPointTo(coordinate))
        return XarmUPathNavigator(self.track, startPos, direction)
    
    def __str__(self) -> str:
        return str(self.track)    

class XarmUPathNavigator:
    def __init__(self, track, startPos, direction:PathDirection = PathDirection.LEFT):
        self.track = track
        self.pos = startPos
        self.direction = direction
        
    def next(self):
        oldPos = self.pos
        if self.direction == PathDirection.RIGHT:
            if self.pos >= len(self.track) - 1:
                self.pos = oldPos - 1
                self.direction = PathDirection.LEFT
            else:
                self.pos = oldPos + 1
        else:
            if self.pos == 0:
                self.pos = oldPos + 1
                self.direction = PathDirection.RIGHT
            else:
                self.pos = oldPos - 1
        return self.track[oldPos]
                
            