import logging

class XarmSpheroEvents:
    def __init__(self, listener = None):
        self.logger = logging.getLogger(__name__)
        self.listener = listener
    
    def _log(self, message):
        self.logger.info(message)  
        
    def spheroDetected(self, position):
        if self.listener:
            self.listener.spheroDetected(position)
        self._log(f"Sphero has been detected") 

    def spheroCatched(self, position):
        if self.listener:
            self.listener.spheroCatched(position)
        self._log("Sphero has been catched")  
    
    def trajectStarted(self, position):
        if self.listener:
            self.listener.trajectStarted(position)
        self._log(f"Traject started at {position}")  
        
    def trajectStopped(self, position):
        if self.listener:
            self.listener.trajectStopped(position)
        self._log(f"Traject stopped at from {position}")  
    
    def movingTo(self, position):
        if self.listener:
            self.listener.movingTo(position)
        self._log(f"Started moving to {position}")  
    
    def arrivingAt(self, position):
        if self.listener:
            self.listener.arrivingAt(position)
        self._log(f"Arrived at {position}")  
    
    def spheroGetFromLoader(self, number):
        if self.listener:
            self.listener.spheroGetFromLoader(number)
        self._log(f"Getting from loader at {number}")  
    
    def spheroDroppedAt(self, position):
        if self.listener:
            self.listener.droppingAt(position)
        self._log(f"Dropping Sphero at {position}")  
        