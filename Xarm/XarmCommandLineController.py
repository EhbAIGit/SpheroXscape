import time
import traceback
from XarmNavigator import XarmNavigator
import threading

def pprint(*args, **kwargs):
    try:
        stack_tuple = traceback.extract_stack(limit=2)[0]
        print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
    except:
        print(*args, **kwargs)

sampleTraject = [(200,0,300),(200,-400,300),(300,-400,300),(300,0,300),(400,0,300),(400,400,300),(300,400,300),(300,0,300),(200,0,300),(200,400,300),(-200,400,300),(-200,200,300),(-300,400,300),(400,400,300)]

class XarmCommandLineController:

    def __init__(self, robotControl:XarmNavigator, startPos=(250, 0, 330)):
        self.robotControl = robotControl
        self.startPos = startPos

    def getNumberInput(self, inputs, pos) :
        rawArgument = inputs[pos]
        if rawArgument.lstrip("-").isnumeric():
            numberInput = int(rawArgument)
            return (True, numberInput)
        else:
            print("Moet een nummer zijn...")
            print(rawArgument)
            return (False,0)

    def positionNumberInputXyz(self, inputs, start = 1):
        if len(inputs) < 4:
            return (False, ())
        else:
            okX, x = self.getNumberInput(inputs, start)
            okY, y = self.getNumberInput(inputs, start + 1)
            okZ, z = self.getNumberInput(inputs, start + 2)
            
            if okX and okY and okZ:
                return (True, (x, y, z))
            else:
                return (False, ())

    def positionInput(self, inputs):
        if len(inputs) >= 2:
            return self.getNumberInput(inputs, 1)
        return False

    def run(self):
        trackingOngoing = False
        
        if self.robotControl.stateIsOk():
            try:
                t: threading.Event = None
                thr:threading.Thread = None
                while True:
                    command = input("> ")
                    inputs = command.split()                 

                    if t:
                        t.set()
                        thr.join()
                        t = None
                        thr = None
  
                    if inputs and len(inputs) >= 1:
                        firstOne = inputs[0]
                        match firstOne.lower():
                            case "q":  print("stopping"); break
                            case "go": self.robotControl.gripOpen()
                            case "gc": self.robotControl.gripClose()
                            case "t":  self.robotControl.moveTraject(sampleTraject)
                            case "r": self.robotControl.recover()
                            case "p":  
                                if len(inputs) == 4:
                                    ok, newPos = self.positionNumberInputXyz(inputs)
                                    if ok:
                                        self.robotControl.movePos(newPos)
                                else:
                                    print(self.robotControl.getCurrentPos())
                            case "s": self.robotControl.goStart()
                            case "x" | "y" | "z":
                                ok, number = self.positionInput(inputs)
                                if ok:
                                    match firstOne:
                                        case "x": self.robotControl.moveXForward(number)
                                        case "y": self.robotControl.moveYForward(number)
                                        case "z": self.robotControl.moveZForward(number)
                            case "px" | "py" | "pz":
                                ok, number = self.positionInput(inputs)
                                if ok:
                                    match firstOne:
                                        case "px": self.robotControl.goX(number)
                                        case "py": self.robotControl.goY(number)
                                        case "pz": self.robotControl.goZ(number)
                            case "gs":
                                ok, number = self.positionInput(inputs)
                                if ok:
                                    self.robotControl.gripLoadPos(number)
                                else:
                                    print(ok, number, "?")
                            case "ds":
                                ok, number = self.positionInput(inputs)
                                if ok:
                                    self.robotControl.dropLoadPos(number)
                                else:
                                    print(ok, number, "?")
                            case "ga":
                                self.robotControl.gripAllLoadPos()
                            case "grip":
                                self.robotControl.gripBasedOnCameraCenter()
                            case "grap":
                                self.robotControl.grip()
                            case "drip":
                                self.robotControl.dropBasedOnCameraCenter()
                            case "drap":
                                self.robotControl.drop()
                            case "trackonce":
                                self.robotControl.moveToClosestSphero()
                            case "track":
                                t = threading.Event()
                                thr = threading.Thread(target = self.robotControl.trackSphero, args={t,})
                                thr.start()
                            case "traject":
                                t = threading.Event()
                                thr = threading.Thread(target = self.robotControl.runTraject, args={t,})
                                thr.start()
                            case _: print("Ongekende opdracht")
            except KeyboardInterrupt:
                print("Programma gestopt door gebruiker.")

    def stop(self):
        self.robotControl.release()