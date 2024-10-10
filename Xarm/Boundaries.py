import shapely
from shapely.geometry import LineString, Point, Polygon

class SquareBoundary:
    
    def __init__(self, xMin, xMax, yMin, yMax, zMin:None, zMax:None):
        self.coords = ((xMin, yMin), (xMin, yMax), (xMax, yMax), (xMax, yMin), (xMin, yMin))
        self.polygon = Polygon(self.coords)
    
    def inside(self, point):
        return shapely.intersects(self.polygon, Point(point))
           
    def outside(self, point):
        return not self.inside(point)
    
    def trajectCrosses(self, start, end):
        return shapely.intersects(self.polygon, LineString([start, end]))
    
    def trajectDoesntCross(self, start, end):
        return not self.trajectCrosses(start, end)

class LineBoundary:
    
    def __init__(self, start, end):
        self.coords = [start, end]
        self.line = LineString(self.coords)
    
    def inside(self, point):
        return shapely.intersects(self.line, Point(point))
           
    def outside(self, point):
        return not self.inside(point)
    
    def trajectCrosses(self, start, end):
        return shapely.intersects(self.line, LineString([start, end]))
    
    def trajectDoesntCross(self, start, end):
        return not self.trajectCrosses(start, end)