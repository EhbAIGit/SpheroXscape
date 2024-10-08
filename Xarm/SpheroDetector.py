import cv2
import pyrealsense2 as rs
import numpy as np
from numpy import ndarray
import time
from collections import namedtuple

class DepthCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)

    def __del__(self):
        self.pipeline.stop()

    def get_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        return depth_frame, color_frame

class TwoDimensionArea:
    def __init__(self, twodarray:ndarray):
        self.twodarray = twodarray
        self.height, self.width = twodarray.shape
        self.xCenter = int(self.height / 2)
        self.yCenter = int(self.width / 2)
        
    def sliceFromPosition(self, distance, pos):
        x, y = pos
        return TwoDimensionArea(self.twodarray[(x - distance):(x + distance),
                                  (y - distance):(y + distance)])

    def sliceFromCenterDeviation(self, distance, deviation):
        x, y = deviation
        return self.sliceFromPosition(distance, (self.xCenter + x, self.yCenter + y))

    def sliceFromCenter(self, distance):
        return self.sliceFromPosition(distance, (self.xCenter, self.yCenter))

    def getArray(self):
        return self.twodarray
    
    def getCenterValue(self):
        return self.twodarray[self.xCenter, self.yCenter]
    
    def check(self, distance, deviation):
        return np.all((self.twodarray >= distance - deviation) & (self.twodarray <= distance + deviation))
        
    def stdDevation(self):
        return np.std(self.twodarray)
    
    def __str__(self):
        result = ''
        for a in self.twodarray:
            for b in a:
                result += "{:.3f} ".format(b)
            result += "\n"
        return result
 
class CircleDetector:
    def __init__(self, minRadius, maxRadius):
        self.minRadius = minRadius
        self.maxRadius = maxRadius
    
    def detectCircle(self, color_image):
        img = cv2.medianBlur(cv2.cvtColor(color_image,cv2.COLOR_BGR2GRAY) , 5)
        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=self.minRadius,maxRadius=self.maxRadius)
        return circles

class SpheroDetector:
    def __init__(self):
        self.dc = DepthCamera()
        #self.circles = CircleDetector(30,40)
        #self.circles = CircleDetector(20,40)
        #self.circles = CircleDetector(78,90) -> based 30 cm
        self.circles = CircleDetector(55, 65) #-> based 40cm
    
    def detectCircles(self):
        depth_frame, color_frame = self.dc.get_frame()

        self.depth_image = np.asanyarray(depth_frame.get_data())
        self.color_image = np.asanyarray(color_frame.get_data())
        
        circles = self.circles.detectCircle(self.color_image)
        
        result = []
        if circles is None:
            return result
        
        converted = np.uint16(np.around(circles))
        
        for i in converted[0,:]:
            x, y, radius = i
            result.append((x, y, radius, (self.depth_image[y, x]))) # w,h

        return result
    
    def depthImage(self):
        return self.depth_image
    
    def colorImage(self):
        return self.color_image

def draw_cross_at(color_image, width, height):
    cv2.line(color_image, (int(width / 2) - 20, int(height / 2)), (int(width / 2) + 20, int(height / 2)), (0, 0, 255), 2)
    cv2.line(color_image, (int(width / 2), int(height / 2) - 20), (int(width / 2), int(height / 2) + 20), (0, 0, 255), 2)

def print_center_image(depth_image, color_image, radius):
    height, width = depth_image.shape
    center = (int(width / 2), int(height / 2))

    # Get the depth value at the center of the depth frame
    depth_center = depth_image[int(height / 2), int(width / 2)]

    # Convert depth value to meters
    distance = depth_center / 10  # Convert mm to meters

    draw_cross_at(color_image, width, height)
    cv2.circle(color_image, center, radius, (0, 0, 255), 2)
    
    print(f"center -> x: {width / 2}, y: {height / 2}, radius: {radius}, depth: {distance}")

    # Display the color frame with the distance on the screen
    cv2.putText(color_image, f"Distance: {distance:.2f} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

import time

class SDetector:
    
    def __init__(self):
        self.sd = SpheroDetector()

    def show_distance_in_center_n(self):
        circles = self.sd.detectCircles()
        color_image = self.sd.colorImage()
        
        height, width = self.sd.depthImage().shape
        h_center = height / 2
        w_center = width / 2
        time.sleep(0.01)
        for i in circles:
            x, y, radius, depth = i
            cv2.circle(color_image,(x,y),radius,(0,255,0),2)
            
            print(f"circle -> x: {x}, y: {y}, radius: {radius}, depth: {depth}")
            
            self.analyze_direction(h_center, w_center, x, y, depth)
        
        print_center_image(self.sd.depthImage(), color_image, 87)    
            
        cv2.imshow('Color Frame', color_image)

    def detectCircle(self):
        circles = self.sd.detectCircles()
        
        height, width = self.sd.depthImage().shape
        h_center = height / 2
        w_center = width / 2
        
        if circles:
            ret = []
            for circle in circles:
                x, y, radius, depth = circle
                deltaX = - (y - h_center) * 60 / 140
                deltaY = - (x - w_center) * 60 / 140
                ret.append((x,y,deltaX, deltaY))
            return ret
        else:
            return None
    
    def analyze_direction(self, h_center, w_center, x, y, depth):
        horizontal_ok = False
        vertical_ok = False
        
        deltaX = - (y - h_center) * 60 / 140
        deltaY = - (x - w_center) * 60 / 140
        
        print(f"real x: {deltaX}")
        print(f"real y: {deltaY}")
        if abs(x - w_center) < 10:
            print("horizontal ok")
            horizontal_ok = True
        elif (x < w_center):
            print("horizontal right")
        else:
            print("horizontal left")
                    
        if abs(y - h_center) < 10:
            print("vertical ok")
            vertical_ok = True
        elif (y < h_center):
            print("vertical down")
        else:
            print("vertical up")
                    
        if vertical_ok and horizontal_ok:
            print(f"position ok at depth {depth}")

class SpheroDetectorFactory:
    def getSpheroDetector(self):
        return SDetector()
    
if __name__ == "__main__":
    
    s = SDetector()
    
    while True:
        s.show_distance_in_center_n()
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()