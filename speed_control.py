"""
Corrected Speed Control
Uses car_run() with different speed values
"""
from microbit import *
import tinybit

def speed_control():
    """Demonstrate speed control with correct API usage"""
    speed_levels = [0, 50, 100, 150, 200, 255]

    display.show(Image.HAPPY)
    sleep(1000)

    for speed in speed_levels:
        display.show(str(speed_levels.index(speed)))

        # Use car_run with different speed values
        if speed > 0:
            tinybit.car_run(speed)
        else:
            tinybit.car_stop()  # Stop at speed 0

        sleep(1000)

    tinybit.car_stop()
    display.show(Image.YES)

if __name__ == "__main__":
    speed_control()
