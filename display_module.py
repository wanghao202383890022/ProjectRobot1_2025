# display_module.py
from microbit import *
import time

class DisplayController:
    """LED Matrix Display Controller"""

    def __init__(self):
        self.number_patterns = {
            0: Image("09990:90009:90009:90009:09990"),
            1: Image("00900:09900:00900:00900:09990"),
            2: Image("09990:00009:09990:90000:09999"),
            3: Image("09990:00009:09990:00009:09990"),
            4: Image("90009:90009:09999:00009:00009"),
            5: Image("09999:90000:09990:00009:09990"),
            6: Image("09990:90000:09990:90009:09990"),
            7: Image("09999:00009:00090:00900:09000"),
            8: Image("09990:90009:09990:90009:09990"),
            9: Image("09990:90009:09990:00009:09990")
        }
        self.system_state = "READY"

    def display_number(self, number):
        """Display a number (0-9) on the LED matrix"""
        try:
            if number in self.number_patterns:
                display.show(self.number_patterns[number])
                sleep(2000)
                return True
            else:
                display.show(Image.SAD)
                print(f"Error: Unsupported number {number}, please use 0-9")
                return False
        except Exception as e:
            display.show(Image.CONFUSED)
            print(f"Display error: {e}")
            return False

    def show_system_status(self, status):
        """Display system status"""
        status_icons = {
            "READY": Image.YES,
            "PROCESSING": Image.ALL_CLOCKS,
            "RECOGNIZED": Image.HAPPY,
            "ERROR": Image.NO
        }

        if status in status_icons:
            display.show(status_icons[status])
            self.system_state = status

    def test_display_all_numbers(self):
        """Test all number displays"""
        try:
            self.show_system_status("PROCESSING")
            sleep(500)

            for i in range(10):
                self.display_number(i)
                sleep(500)

            self.show_system_status("READY")
            print("Display test completed")
            return True

        except Exception as e:
            self.show_system_status("ERROR")
            print(f"Display test failed: {e}")
            return False

# Standalone test function
def test_display_functionality():
    """Display functionality test"""
    controller = DisplayController()
    return controller.test_display_all_numbers()

if __name__ == "__main__":
    test_display_functionality()
