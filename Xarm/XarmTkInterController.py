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
