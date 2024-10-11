import time
import traceback

try:
    from xarm.tools import utils
except:
    pass
from xarm import version
from xarm.wrapper import XArmAPI


def pprint(*args, **kwargs):
    try:
        stack_tuple = traceback.extract_stack(limit=2)[0]
        print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
    except:
        print(*args, **kwargs)

class XarmDriver:
    def __init__(self, ip='10.2.172.20'):
        pprint('xArm-Python-SDK Version:{}'.format(version.__version__))

        self.arm = XArmAPI(ip)
        self.arm.clean_warn()
        self.arm.clean_error()
        self.arm.motion_enable(True)
        self.arm.set_mode(0)
        self.arm.set_state(0)
        time.sleep(1)

        self.variables = {}
        self.params = {'speed': 100, 'acc': 2000, 'angle_speed': 20, 'angle_acc': 500, 'events': {}, 'variables': self.variables, 'callback_in_thread': True, 'quit': False}

        self.speedParameter = 100
        self.accParameter = 2000
        self.angleSpeedParameter = 20
        self.angleAccParameter = 500

        self.arm.register_error_warn_changed_callback(self.error_warn_change_callback)
        self.arm.register_state_changed_callback(self.state_changed_callback)
                
        if hasattr(self.arm, 'register_count_changed_callback'):
            self.arm.register_count_changed_callback(self.count_changed_callback)
            
        self.arm.register_connect_changed_callback(self.connect_changed_callback)
        
    def recover(self):
        self.arm.clean_warn()
        self.arm.clean_error()
        self.arm.motion_enable(True)
        self.arm.set_mode(0)
        self.arm.set_state(0)
        time.sleep(1)
    
    def getLivePosition(self):    
        livePos = self.arm.position
        return (livePos[0], livePos[1], livePos[2])

    def error_warn_change_callback(self, data):
        if data and data['error_code'] != 0:
            self.params['quit'] = True
            pprint('err={}, quit'.format(data['error_code']))
            self.arm.release_error_warn_changed_callback(self.error_warn_change_callback)

    def state_changed_callback(self, data):
        if data and data['state'] == 4:
            if self.arm.version_number[0] > 1 or (self.arm.version_number[0] == 1 and self.arm.version_number[1] > 1):
                self.params['quit'] = True
                pprint('state=4, quit')
                self.arm.release_state_changed_callback(self.state_changed_callback)

    def count_changed_callback(self, data):
        if not self.params['quit']:
            pprint('counter val: {}'.format(data['count']))

    def connect_changed_callback(self, data):
        if data and not data['connected']:
            self.params['quit'] = True
            pprint('disconnect, connected={}, reported={}, quit'.format(data['connected'], data['reported']))
            self.arm.release_connect_changed_callback(self.error_warn_change_callback)

    def initPos(self, coordinate):
        x, y, z = coordinate
        if self.arm.error_code == 0 and not self.params['quit']:
            self.code = self.arm.set_position(*[x, y, z, 180.0, 0.0, 0.0], speed=self.params['speed'], mvacc=self.params['acc'], radius=-1.0, wait=True)

    def gripOpen(self):
        return self.arm.set_cgpio_analog(0, 0)
    
    def getAngle(self):
        return self.arm.get_servo_angle()
        
 
    def gripClose(self):
        return self.arm.set_cgpio_analog(0, 5)
    
    def stateIsOk(self):
        return self.arm.error_code == 0 and not self.params['quit']

    def release(self):
        if hasattr(self.arm, 'release_count_changed_callback'):
            self.arm.release_count_changed_callback(self.count_changed_callback)
        self.arm.release_error_warn_changed_callback(self.state_changed_callback)
        self.arm.release_state_changed_callback(self.state_changed_callback)
        self.arm.release_connect_changed_callback(self.error_warn_change_callback)