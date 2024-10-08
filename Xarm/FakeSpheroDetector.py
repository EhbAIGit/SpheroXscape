class FakeSpheroDetector:
    
    def detectCircle(self):
        return None

class SpheroDetectorFactory:
    def getSpheroDetector(self):
        return FakeSpheroDetector()