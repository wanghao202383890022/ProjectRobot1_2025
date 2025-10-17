"""
Corrected Direction Control
Uses TinyBit's directional control API functions
"""
from microbit import *
import tinybit

def direction_control():
    """Execute 6-direction movement with correct API calls"""
    # Movement sequence with proper TinyBit functions
    movements = [
        (Image.ARROW_S, tinybit.car_run, 150),      # Forward
        (Image.ARROW_N, tinybit.car_back, 150),     # Backward
        (Image.ARROW_W, tinybit.car_left, 150),     # Left
        (Image.ARROW_E, tinybit.car_right, 150),    # Right
        (Image.ARROW_W, tinybit.car_spinleft, 200), # Spin left
        (Image.ARROW_E, tinybit.car_spinright, 200) # Spin right
    ]

    for icon, move_func, speed in movements:
        display.show(icon)
        move_func(speed)  # Correct API call
        sleep(1000)
        tinybit.car_stop()  # Correct stop function
        sleep(300)

    display.show(Image.YES)

if __name__ == "__main__":
    direction_control()
