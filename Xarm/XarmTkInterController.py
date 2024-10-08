"""
# Import Module 
from tkinter import *
import time 
from threading import *
  
# Create Object 
root = Tk() 
root.geometry("800x800") 

leftframe = Frame(root)  
leftframe.pack(side = LEFT)  
  
rightframe = Frame(root)  
rightframe.pack(side = RIGHT)  


  
# Set geometry 

def startWork():
    t = Thread(target=work)
    t.start()
  
def work(): 
  
    print("sleep time start") 
    
    for i in range(10): 
        print("0-" + str(i)) 
        time.sleep(1) 
  
    print("sleep time stop") 


def work1(): 
  
    print("sleep time start") 
  
    for i in range(10): 
        print("1-" + str(i)) 
        time.sleep(1) 
  
    print("sleep time stop") 


  
# Create Button 
Button(leftframe, text="Move", command=startWork).pack(side = TOP) 
Button(leftframe, text="Traject", command=work1).pack(side =TOP) 

  
# Execute Tkinter 
root.mainloop() 
""" 

# Import Module 
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
        
        
        Button(self.leftframe, text="Test", command=self.work).pack(side =TOP)
        Button(self.leftframe, text="Traject", command=self.traject).pack(side =TOP) 
        Button(self.leftframe, text="Stop traject", command=self.stopTraject).pack(side =TOP) 
    
    def run(self):
        self.root.mainloop() 
        
    def traject(self):
        self.t = Event()
        self.thr = Thread(target = self.robotControl.runTraject, args={self.t,})
        self.thr.start()
    
    def stopTraject(self):
        self.t.set()
  
    def work(self): 
        self.robotControl.moveXForward(50)
         
# Execute Tkinter 
