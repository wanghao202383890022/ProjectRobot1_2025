"""
Corrected Path Control Module
Fully implements Part 4.5: Path Control requirements
Supports L, O, D, Z letter path patterns with complete functionality
"""
from microbit import *
import tinybit

class PathController:
    def __init__(self):
        """
        Initialize path control system with four predefined patterns
        Each pattern consists of movement sequences forming letters
        """
        self.path_definitions = {
            'L': [
                ('forward', 1000),    # Vertical movement for L
                ('left', 500)         # Horizontal movement for L
            ],
            'O': [
                ('forward', 800), ('right', 400),
                ('forward', 800), ('right', 400),
                ('forward', 800), ('right', 400),
                ('forward', 800), ('right', 400)  # Complete square for O
            ],
            'D': [
                ('forward', 1000),    # Vertical stroke for D
                ('right', 300)        # Curved movement for D
            ],
            'Z': [
                ('forward', 500), ('right', 300),
                ('forward', 500), ('left', 300),
                ('forward', 500)      # Zigzag pattern for Z
            ]
        }
        self.available_paths = list(self.path_definitions.keys())
        self.current_path_index = 0
        self.current_path = self.available_paths[0]

    def execute_movement(self, action, duration):
        """
        Execute individual movement action with proper TinyBit API
        Supports four basic movement types
        """
        movement_functions = {
            'forward': (Image.ARROW_S, tinybit.car_run, 150),
            'backward': (Image.ARROW_N, tinybit.car_back, 150),
            'left': (Image.ARROW_W, tinybit.car_left, 150),
            'right': (Image.ARROW_E, tinybit.car_right, 150)
        }

        if action in movement_functions:
            display_icon, move_func, speed = movement_functions[action]
            display.show(display_icon)
            move_func(speed)
            sleep(duration)
            tinybit.car_stop()

    def switch_path(self):
        """Cycle through available path patterns"""
        self.current_path_index = (self.current_path_index + 1) % len(self.available_paths)
        self.current_path = self.available_paths[self.current_path_index]
        display.show(self.current_path)
        sleep(800)

    def execute_current_path(self):
        """Execute complete movement sequence for selected path"""
        display.show(self.current_path)
        sleep(1000)

        # Execute each action in the current path
        for action, duration in self.path_definitions[self.current_path]:
            self.execute_movement(action, duration)
            sleep(200)  # Brief pause between movements

        # Path completion confirmation
        display.show(Image.YES)
        sleep(1000)

def main_path_control():
    """
    Main control loop for path control system
    Handles button interactions and path execution
    """
    controller = PathController()

    # System initialization
    display.show(Image.HAPPY)
    sleep(1000)
    display.show(controller.current_path)

    while True:
        # Button A: Path selection
        if button_a.was_pressed():
            controller.switch_path()

        # Button B: Path execution
        if button_b.was_pressed():
            controller.execute_current_path()

        # Display current path selection
        display.show(controller.current_path)
        sleep(100)

# Program entry point
if __name__ == "__main__":
    main_path_control()
