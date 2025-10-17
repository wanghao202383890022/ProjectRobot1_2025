"""
Corrected Basic Movement Control
Uses proper TinyBit API: car_run() and car_stop()
"""
from microbit import *
import tinybit

def move_car():
    """Control robot forward movement with correct TinyBit API"""
    display.show(Image.ARROW_S)
    sleep(1000)

    # Correct API usage: car_run for forward movement
    tinybit.car_run(150)  # Both motors at speed 150
    sleep(2000)

    # Correct API usage: car_stop to stop motors
    tinybit.car_stop()

    display.show(Image.YES)

if __name__ == "__main__":
    move_car()
