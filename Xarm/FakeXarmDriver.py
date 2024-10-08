import queue
import turtle
from Constants import START_POS

class FakeXarmDriver:
    def __init__(self, turtle):
        self.t = turtle
        self.size = 1000
        self.initTurtle()

    def initTurtle(self):
        self.t.screen.setup(self.size, self.size)

        self.t.hideturtle()
        self.t.speed(0)
        self.drawSquareAroundCenter(800)
        self.drawSquareAroundCenter(100)
        
        self.t.up()
        self.t.showturtle()
        self.t.speed(1)
        self.initPos(START_POS)
        
    def getLivePosition(self):
        return (self.x, self.y, self.z)
        
    def drawSquareAroundCenter(self, s):
        self.drawRectangle((-s // 2, s // 2), s, s)

    def drawRectangle(self, start, w, h):
        x, y = start
        self.t.up()
        self.t.setpos(x, y)
        self.t.down()
        self.t.forward(w)
        self.t.right(90)
        self.t.forward(h)
        self.t.right(90)
        self.t.forward(w)
        self.t.right(90)
        self.t.forward(h)
        self.t.right(90)
        self.x = x
        self.y = y
        self.z = 400
    
    def initPos(self, coordinate):
        x, y, z = coordinate
        self.t.setpos(y, x)
        self.x = x
        self.y = y
        self.z = z

    def gripOpen(self):
        print("grip open")
        return 0

    def gripClose(self):
        print("grip close")
        return 0

    def goToBasePosition(self):
        return 0

    def stateIsOk(self):
        return True

    def release(self):
        pass
    
    def recover(self):
        pass

class ThreadSafeWrapper:
    def __init__(self, fakeXarmDriver: FakeXarmDriver):
        self.fakeXarmDriver = fakeXarmDriver
        self.graphics = queue.Queue(1)
        self.turtle = fakeXarmDriver.t
        self.process_queue()
    
    def initTurtle(self):
        self.fakeXarmDriver.initTurtle()
        
    def getLivePosition(self):
        return self.fakeXarmDriver.getLivePosition()

    def process_queue(self):
        while not self.graphics.empty():
            coordinate = self.graphics.get()
            self.fakeXarmDriver.initPos(coordinate)

        turtle.ontimer(self.process_queue, 100)
        
    def initPos(self, coordinate):
        self.graphics.put(coordinate)

    def gripOpen(self):
        return self.fakeXarmDriver.gripOpen()

    def gripClose(self):
        return self.fakeXarmDriver.gripClose()

    def goToBasePosition(self):
        return self.fakeXarmDriver.goToBasePosition()

    def stateIsOk(self):
        return self.fakeXarmDriver.stateIsOk()

    def release(self):
        return self.fakeXarmDriver.release()
    
    def recover(self):
        return self.fakeXarmDriver.recover()
