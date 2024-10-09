import time
import traceback

import pygame

from XarmNavigator import XarmNavigator


def pprint(*args, **kwargs):
    try:
        stack_tuple = traceback.extract_stack(limit=2)[0]
        print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
    except:
        print(*args, **kwargs)

class XarmGamePadController:
    
    def __init__(self, robotControl:XarmNavigator, startPos=(250, 0, 330)):
        self.robotControl = robotControl
        self.startPos = startPos
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("Geen joystick gevonden.")
            quit()

    def run(self):
        if self.robotControl.stateIsOk():
            try:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()

                while True:
                    pygame.event.pump()

                # Lees de invoer van de joystick uit
                    y_axis = joystick.get_axis(0)  
                    x_axis = joystick.get_axis(1)  # Y-as

                    button1 = joystick.get_button(0)
                    button2 = joystick.get_button(1)
                    button3 = joystick.get_button(2)
                    button4 = joystick.get_button(3)                   
                    
                    time.sleep(0.1)
                    
                    X_SPEED = 20
                    Y_SPEED = 20
                    Z_SPEED = 5

                    if (x_axis >= 0.1) :  
                        self.robotControl.moveXBackward(X_SPEED)
                    elif (x_axis < -0.1) :  
                        self.robotControl.moveXForward(X_SPEED)
                    elif (y_axis > 0.1) :  
                        self.robotControl.moveYForward(Y_SPEED)
                    elif (y_axis < -0.1) :  
                        self.robotControl.moveYBackward(Y_SPEED)
                    elif (button1 == 1) :
                        self.robotControl.moveZForward(Z_SPEED)
                    elif (button2 == 1):
                        self.robotControl.gripOpen()
                    elif (button3 == 1) :
                        self.robotControl.moveZBackward(Z_SPEED)
                    elif (button4 == 1) :
                        self.robotControl.gripClose()
            except KeyboardInterrupt:
                print("Programma gestopt door gebruiker.")
            self.robotControl.release()

# from turtle import Turtle
# from FakeXarmDriver import FakeXarmDriver
# from XarmNavigator import XarmNavigator
# from XarmDriver import XarmDriver

# # t = Turtle()
# # f = FakeXarmDriver(t)

# f = XarmDriver()
# n = XarmNavigator(f)
# x = XarmGamePadController(n)

# x.run() 