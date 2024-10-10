import logging
import paho.mqtt.client as mqtt
import json
from Constants import *
import random

class XarmSpheroEventsMqtt:
    def __init__(self, listener = None):
        self.logger = logging.getLogger(__name__)
        self.listener = listener
        self.clientId = f'python-mqtt-{random.randint(0, 1000)}'
        self.mqtt = mqtt.Client(client_id=self.clientId, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt.on_connect = self.onConnect
        self.mqtt.connect(MQTT_HOST, MQTT_PORT)
        
    def createMessage(self, code, position, payload):
        message = {
            'code' : code,
            'position' : position,
            'payload' : payload
        }
        return json.dumps(message)
    
    def onConnect(self, client, userdata, flags, rc, props):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
        

    def sendMessage(self, code, position, payload):
        messageAsJson = self.createMessage(code, position, payload)
        self.logger.info(messageAsJson)
        self.mqtt.publish(topic=MQTT_TOPIC, payload = messageAsJson)
    
    def applicationStarted(self, position):
        self.sendMessage(0, position, "Sphero-tracker started")

    def spheroDetected(self, position):
        self.sendMessage(5, position, "Lost track of Sphero")
    
    def spheroLost(self, position):
        self.sendMessage(4, position, "Sphero discovered")

    def spheroCatched(self, position):
        self.sendMessage(6, position, "Sphero catched")
 
    def trajectStarted(self, position):
        self.sendMessage(2, position, "Traject and scanning has started")
      
    def trajectStopped(self, position):
        self.sendMessage(3, position, "Traject and scanning has stopped")
    
    def movingTo(self, position):
        pass
    
    def arrivingAt(self, position):
        pass
  
    def spheroGetFromLoader(self, number):
        pass
    
    def spheroDroppedAt(self, position):
        pass

    def spheroDroppedAtLoader(self, position, loader):
        self.sendMessage(7, position, f"Placing Sphero {loader} back at location")

    def gettingSpherosFromLoadstation(self, position):
        self.sendMessage(1, position, "Positioning Sphero's from load")