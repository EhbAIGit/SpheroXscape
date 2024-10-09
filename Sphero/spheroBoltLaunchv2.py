import pygame
import time
import sys
from spherov2 import scanner
from spherov2.types import Color
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.commands.power import Power
import paho.mqtt.client as mqtt
import math

'''
SB-9DD8 1
SB-2BBE 2
SB-27A5 3
SB-81E0 4
SB-7740 5
'''


class SpheroController:
    def __init__(self, joystick, color, ball_number):
        self.toy = None
        self.speed = 50
        self.heading = 0
        self.base_heading = 0
        self.is_running = True
        self.calibration_mode = False
        self.joystick = joystick
        self.last_command_time = time.time()
        self.heading_reset_interval = 1
        self.last_heading_reset_time = time.time()
        self.threshold_accel_mag = 0.05
        self.collision_occurred = False
        self.color = color  # Store the color parameter
        self.previous_button = 1
        self.number = ball_number  # Assign the ball number
        self.gameStartTime = time.time()
        self.gameOn = False
        self.boosterCounter = 0
        self.calibrated =  False

        # MQTT instellen
        self.mqtt_broker = "broker.emqx.io"
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.mqtt_broker)
        self.mqtt_topic = "sphero/ball_status"

    def send_mqtt_message(self,topic, message):
        # Verzend het MQTT-bericht
        self.mqtt_client.loop_start()  # Start de loop
        print (f" mqtt send to {self.mqtt_broker} on topic {topic} : {message}")
        self.mqtt_client.publish(topic, message)
        self.mqtt_client.loop_stop()  # Stop de loop



    def discover_nearest_toy(self):
        try:
            # Scan voor alle beschikbare Sphero's
            toys = scanner.find_toys()
            
            # Controleer of er Sphero's zijn gevonden
            if not toys:
                print("Geen Sphero's gevonden.")
                return
            
            # Neem de eerste Sphero aan als de dichtstbijzijnde (afhankelijk van de scanner)
            self.toy = toys[0]
            print(f"Dichtstbijzijnde Sphero toy '{self.toy.name}' ontdekt.")            
            return self.toy.name
        except Exception as e:
            print(f"Error no toys nearby: {e}")
        
    
    def discover_toy(self, toy_name):
        try:
            self.toy = scanner.find_toy(toy_name=toy_name)
            print(f"Sphero toy '{toy_name}' discovered.")
                
        except Exception as e:
            print(f"Error discovering toy: {e}")

    def connect_toy(self):
        if self.toy is not None:
            try:
                return SpheroEduAPI(self.toy)
            except Exception as e:
                print(f"Error connecting to toy: {e}")
        else:
            print("No toy discovered. Please run discover_toy() first.")
            return None

    def move(self, api, heading, speed):
        api.set_heading(heading)
        api.set_speed(speed)

    def toggle_calibration_mode(self, api, Y):
        if not self.calibration_mode:
            self.enter_calibration_mode(api, Y)
        else:
            self.exit_calibration_mode(api)

    def enter_calibration_mode(self, api, X):
        api.set_speed(0)
        # print("Calibration mode activated.")
        #self.gameStartTime = time.time()
        self.gameStartTime = time.time()
        self.calibration_mode = True
        self.gameOn = False
        api.set_front_led(Color(255, 0, 0))

        # Get the current heading angle
        self.base_heading = api.get_heading()

        # Determine the new heading based on Y value
        if X < -0.7:
            new_heading = self.base_heading - 5  # Turn +5 degrees
        elif X > 0.7:
            new_heading = self.base_heading + 5  # Turn -5 degrees
        else:
            new_heading = self.base_heading

        # Rotate the Sphero to the new heading
        api.set_heading(new_heading)

    def exit_calibration_mode(self, api):
        self.calibrated = True
        self.send_mqtt_message("sphero/ball_status",f"New player started: {self.number}")
        self.calibration_mode = False
        self.gameOn = True
        self.boosterCounter = 0
        self.gameStartTime = time.time()
        api.set_front_led(Color(0, 255, 0))


    # Define LED patterns for each number
    LED_PATTERNS = {
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5'
    }

    # Method to set LED pattern for a specific number
    def set_number(self, number):
        self.number = int(number)

    # Method to display number on LED matrix
    def display_number(self, api):
        number_char = self.LED_PATTERNS.get(self.number)
        if number_char:
            api.set_matrix_character(number_char, self.color)
        else:
            print (f"Error in matrix '{self.number}'")

    def print_battery_level(self, api):
        battery_voltage = Power.get_battery_voltage(self.toy)
        print(f"Battery status of {self.number}: {battery_voltage} V ")
        if (battery_voltage < 3.9):
            self.send_mqtt_message("sphero/ball_status/warning",f"Warning:  Battery for number {self.number} is low ({battery_voltage} Volt)")
        if (battery_voltage < 3.7):
            self.send_mqtt_message("sphero/ball_status/warning",f"ERROR:  Battery for number {self.number} is critical ({battery_voltage} Volt), replace it!")
        if (battery_voltage < 4.2):
            self.send_mqtt_message("sphero/ball_status/warning",f"ERROR:  {self.number} has been shut down because battery went down!")
            exit("Battery")


    def control_toy(self):
        lower_than_negative_threshold_time = None
        higher_than_positive_threshold_time = None
        try:
            with self.connect_toy() as api:
                last_battery_print_time = time.time()  # Initialize the last battery print time
                last_timePassed_print_time = time.time()
                self.set_number(self.number)
                self.display_number(api)
                #self.gameStartTime = time.time()
                #self.gameOn = True

                while self.is_running:
                    pygame.event.pump()
                    if (self.gameOn == False):
                        self.gameStartTime = time.time()                        
                    current_time2 = time.time()
                    gameTime = current_time2 - self.gameStartTime    

                    if current_time2 - last_battery_print_time >= 60:
                        self.print_battery_level(api)
                        last_battery_print_time = current_time2  # Update the last battery print time
                    
                    
                    if (self.gameOn == True and gameTime > 310):
                        self.send_mqtt_message("sphero/ball_status",f" Player {self.number} won! It's ball survived for 5 minutes")
                        self.gameOn = False
                        self.gameStartTime = time.time()
                        #self.toggle_calibration_mode(api, X)  # Pass Y value to toggle_calibration_mode
                        exit()
                        
                    
                    if (current_time2 - last_timePassed_print_time >=60):
                        seconds = (current_time2 - self.gameStartTime)
                        minutes = seconds/60
                        minutes = int(minutes)
                        if (minutes >= 1 and minutes <=3) :
                            self.send_mqtt_message("sphero/ball_status/timing",f"{5-minutes} minuten left for player {self.number}")
                            last_timePassed_print_time = time.time()
                        if (minutes ==4 ):
                            self.send_mqtt_message("sphero/ball_status/timing",f"1 minute left player {self.number}")
                            last_timePassed_print_time = time.time()
                
                    if (self.gameOn == True):
                        acceleration_data = api.get_acceleration()
                        if acceleration_data is not None:
                            x_acc = acceleration_data['x']
                            z_acc = acceleration_data['z']
                            
                            # Calculate the angle in degrees
                            angle = math.degrees(math.atan2(x_acc, z_acc))
                            #print(f"Current angle: {angle:.2f} degrees")

                            # Check if the angle exceeds 10 degrees
                            if abs(angle) >= 30:
                                hillCounter+=1
                                if (hillCounter > 10):
                                    seconds = (current_time2 - self.gameStartTime)

                                    self.send_mqtt_message("sphero/ball_status",f" Player {self.number} lost! It's ball survived {seconds:.2f} seconds")
                                    self.gameOn = False
                                    self.gameStartTime = time.time()
                                    exit()
                                    #self.toggle_calibration_mode(api, X)  # Pass Y value to toggle_calibration_mode
                            else:
                                #print("Sphero is on a flat surface.")
                                hillCounter=0
                        else:
                            print("Acceleration data is not available.")
                    
                    X = self.joystick.get_axis(0)
                    Y = self.joystick.get_axis(1)
                    boosterButton =  self.joystick.get_button(2)
                    MoveButton = self.joystick.get_button(0) 
                    button_x = self.joystick.get_button(1)  # Assuming X button is at index 0
                    if button_x == 0 and self.previous_button == 1 and self.calibrated == False:
                        self.toggle_calibration_mode(api, X)  # Pass Y value to toggle_calibration_mode
                    self.previous_button = button_x 

                    if self.calibration_mode:
                        self.enter_calibration_mode(api, X)  # Call enter_calibration_mode with Y value
                    else:
                        # Your movement logic based on joystick axes here
                        if MoveButton == 1 :
                            self.move(api, self.base_heading, self.speed)
                        elif boosterButton == 1 and self.boosterCounter < 5:
                            self.move(api,self.base_heading, 100)
                            self.boosterCounter +=1
                            time.sleep(0.5)
                            if (self.boosterCounter == 1 ) : self.send_mqtt_message("sphero/ball_status",f"Player {self.number} has used it's first booster!")
                            if (self.boosterCounter == 4 ) : self.send_mqtt_message("sphero/ball_status",f"Player {self.number} has used it's last booster!")

                        elif Y < -0.7:
                            self.move(api, self.base_heading - 180, self.speed)  # Left
                        elif Y > 0.7:
                            self.move(api, self.base_heading + 180, self.speed)  # Right
                        elif X > 0.7:
                            self.move(api, self.base_heading + 22, 0)  # Up
                        elif X < -0.7:
                            self.move(api, self.base_heading - 22, 0)  # Down
                        else:
                            api.set_speed(0)  # Stop       
                    self.base_heading = api.get_heading()

        finally:
            pygame.quit()  # Make sure to quit pygame when done

def main(toy_name = None, joystickID = 0, playerID = 1):
    # Initialize pygame and joysticks
    pygame.init()
    pygame.joystick.init()
    
    mqtt_broker = "emqx.broker.io"  # Vervang door je MQTT-broker adres
    mqtt_topic = "sphero/ball_status"  # Vervang door je gewenste topic


    # Check for a connected joystick
    num_joysticks = pygame.joystick.get_count()
    if num_joysticks == 0:
        print("No joysticks found.")
        return

    # Get the specified joystick
    joystick = pygame.joystick.Joystick(joystickID)
    joystick.init()

    # Define a color for the Sphero
    sphero_color = Color(255, 0, 0)  # Red

    # Create a SpheroController instance
    sphero_controller = SpheroController(joystick, sphero_color, playerID)
    
    if (toy_name == 'Any'):
        toy_name = sphero_controller.discover_nearest_toy()

    sphero_controller.discover_toy(toy_name)

    if sphero_controller.toy:
        sphero_controller.control_toy()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py <toy_name/or Any> <joystickNumber 0-1> <player 1-5>")
        sys.exit(1)
    
    toy_name = sys.argv[1]
    joystick = int(sys.argv[2])
    playerid = int(sys.argv[3])
    print(f"Try to connect to: {toy_name} with number  {joystick} for player {playerid}")
    
    main(toy_name, joystick, playerid)
