from XarmNavigator import XarmNavigator
from XarmSpheroEvents import XarmSpheroEvents
import argparse
import logging

def createSimulationEnvironment():
    from turtle import Turtle
    from FakeXarmDriver import FakeXarmDriver
    from FakeXarmDriver import ThreadSafeWrapper
    return ThreadSafeWrapper(FakeXarmDriver(Turtle()))

def createRealEnvironment():
    from XarmDriver import XarmDriver
    return XarmDriver()

def createController(navigator):
    from XarmGamePadController import XarmGamePadController
    return XarmGamePadController(navigator)

def createCommandLineController(navigator):
    from XarmCommandLineController import XarmCommandLineController
    return XarmCommandLineController(navigator)

def createTkInterController(navigator):
    from XarmTkInterController import XarmTkInterController
    return XarmTkInterController(navigator)

def selectDriver(args):
    return createRealEnvironment() if args.environment == "real" \
            else createSimulationEnvironment() if args.environment == "simulated" \
            else createRealEnvironment()
            
def createRealCamera():
    from SpheroDetector import SpheroDetectorFactory
    return SpheroDetectorFactory()

def createFakeCamera():
    from FakeSpheroDetector import SpheroDetectorFactory
    return SpheroDetectorFactory()

def selectCamera(args):
    return createRealCamera() if args.environment == "real" \
            else createFakeCamera() if args.environment == "simulated" \
            else createRealCamera()

def selectController(args):
    return createCommandLineController(navigator) if args.controller == "keyboard" \
                    else createController(navigator) if args.controller == "simulated" \
                    else createTkInterController(navigator) if args.controller == "gui" \
                    else createCommandLineController(navigator)

def selectEvents(args):
    if args.mqtt == "yes":
        from XarmSpheroEventsMqtt import XarmSpheroEventsMqtt
        return XarmSpheroEvents(XarmSpheroEventsMqtt())
    return XarmSpheroEvents()
    

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--controller", choices=["keyboard", "gui","gamepad"], default="keyboard")
    parser.add_argument("-e", "--environment", choices=["real", "simulated"], default="real")
    parser.add_argument("-m", "--mqtt", choices=["yes", "no"], default="no")

    args = parser.parse_args()

    driver = selectDriver(args)
    events = selectEvents(args)
    cameraFactory = selectCamera(args)
    navigator = XarmNavigator(driver, cameraFactory, events)
    controller = selectController(args)
    
    controller.run()