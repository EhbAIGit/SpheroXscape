import pygame
import time
import sys
from spherov2 import scanner
from spherov2.types import Color
from spherov2.sphero_edu import SpheroEduAPI
from spherov2.commands.power import Power

'''
python /home/ubuntu/ILSF2024/SpheroBolt/spheroBoltLaunch.py SB-9DD8 1
python /home/ubuntu/ILSF2024/SpheroBolt/spheroBoltLaunch.py SB-2BBE 2
python /home/ubuntu/ILSF2024/SpheroBolt/spheroBoltLaunch.py SB-27A5 3
python /home/ubuntu/ILSF2024/SpheroBolt/spheroBoltLaunch.py SB-81E0 4
python /home/ubuntu/ILSF2024/SpheroBolt/spheroBoltLaunch.py SB-7740 5
'''

class SpheroController:
    def __init__(self, joystick, color, ball_number):
        self.toy = None
        self.speed = 30
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
        print("Calibration mode activated.")
        self.calibration_mode = True
        api.set_front_led(Color(255, 0, 0))

        # Get the current heading angle
        self.base_heading = api.get_heading()

        # Determine the new heading based on Y value
        if X < -0.7:
            new_heading = self.base_heading - 10  # Turn +5 degrees
        elif X > 0.7:
            new_heading = self.base_heading + 10  # Turn -5 degrees
        else:
            new_heading = self.base_heading

        # Rotate the Sphero to the new heading
        api.set_heading(new_heading)

    def exit_calibration_mode(self, api):
        print("Exiting calibration mode.")
        self.calibration_mode = False
        api.set_front_led(Color(0, 255, 0))

    # Define LED patterns for each number
    LED_PATTERNS = {
        1: '1',
        2: '2',
        3: '3',
        4: '4'
    }

    # Method to set LED pattern for a specific number
    def set_number(self, number):
        self.number = number

    # Method to display number on LED matrix
    def display_number(self, api):
        number_char = self.LED_PATTERNS.get(self.number)
        if number_char:
            api.set_matrix_character(number_char, self.color)

    def print_battery_level(self, api):
        battery_voltage = Power.get_battery_voltage(self.toy)
        print(battery_voltage)

    def control_toy(self):
        lower_than_negative_threshold_time = None
        higher_than_positive_threshold_time = None
        try:
            with self.connect_toy() as api:
                last_battery_print_time = time.time()  # Initialize the last battery print time

                while self.is_running:
                    pygame.event.pump()

                    current_time2 = time.time()
                    if current_time2 - last_battery_print_time >= 45:
                        self.print_battery_level(api)
                        last_battery_print_time = current_time2  # Update the last battery print time

                    acceleration_data = api.get_acceleration()
                    if acceleration_data is not None:
                        z_acceleration = acceleration_data['z']
                        x_acceleration = acceleration_data['x']
                        y_acceleration = acceleration_data['y']
                        if x_acceleration < -0.7:
                            lower_than_negative_threshold_time = int(time.time())
                        if x_acceleration > 0.7:
                            higher_than_positive_threshold_time = int(time.time())

                        if lower_than_negative_threshold_time is not None and higher_than_positive_threshold_time is not None:
                            time_difference = abs(higher_than_positive_threshold_time - lower_than_negative_threshold_time)
                            if time_difference <= 10:
                                print(f"Ball Name: {self.toy.name} was LIFTED UP")
                                lower_than_negative_threshold_time = None
                                higher_than_positive_threshold_time = None
                    else:
                        print("Acceleration data is not available.")
                    
                    X = self.joystick.get_axis(0)
                    Y = self.joystick.get_axis(1)
                    MoveButton = self.joystick.get_button(5) 
                    button_x = self.joystick.get_button(0)  # Assuming X button is at index 0
                    if button_x == 0 and self.previous_button == 1:
                        self.toggle_calibration_mode(api, X)  # Pass Y value to toggle_calibration_mode
                    self.previous_button = button_x 

                    if self.calibration_mode:
                        self.enter_calibration_mode(api, X)  # Call enter_calibration_mode with Y value
                    else:
                        # Your movement logic based on joystick axes here
                        if MoveButton == 1 :
                            self.move(api, self.base_heading, self.speed)
                        elif Y < -0.7:
                            self.move(api, self.base_heading - 180, self.speed)  # Left
                        elif Y > 0.7:
                            self.move(api, self.base_heading + 180, self.speed)  # Right
                        elif X > 0.7:
                            self.move(api, self.base_heading + 45, self.speed)  # Up
                        elif X < -0.7:
                            self.move(api, self.base_heading - 45, self.speed)  # Down
                        else:
                            api.set_speed(0)  # Stop       
                    self.base_heading = api.get_heading()
                    self.set_number(self.number)
                    self.display_number(api)

        finally:
            pygame.quit()  # Make sure to quit pygame when done

def main(toy_name, joystickID):
    # Initialize pygame and joysticks
    pygame.init()
    pygame.joystick.init()

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
    sphero_controller = SpheroController(joystick, sphero_color, joystickID)

    sphero_controller.discover_toy(toy_name)

    if sphero_controller.toy:
        sphero_controller.control_toy()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <toy_name> <joystickID>")
        sys.exit(1)

    toy_name = sys.argv[1]
    joystickID = int(sys.argv[2])
    main(toy_name, joystickID)
