# main.py - Micro:bit Face Recognition System Main Program
from microbit import *
import time
import os

# Import custom modules
try:
    from display_module import DisplayController
    from face_recognition import FaceRecognitionSystem
    from security_manager import SecureFaceRecognitionSystem, DataSecurityManager
except ImportError as e:
    # Handle module import failure
    display.show(Image.SAD)
    print(f"Module import error: {e}")
    sleep(2000)

class MicrobitFaceSystem:
    """Micro:bit Face Recognition Main System Class"""

    def __init__(self):
        """Initialize system state and components"""
        self.system_state = "BOOTING"
        self.current_number = 0
        self.error_count = 0
        self.setup_complete = False

        # System components
        self.display_controller = None
        self.recognition_system = None

        self.initialize_system()

    def initialize_system(self):
        """Initialize all system components"""
        try:
            print("=== System Initialization Started ===")

            # Show startup animation
            self.show_startup_animation()

            # Initialize display controller
            self.display_controller = DisplayController()
            print("✓ Display controller initialized")

            # Initialize recognition system
            self.recognition_system = SecureFaceRecognitionSystem()
            print("✓ Face recognition system initialized")

            # Test basic functionality
            self.test_basic_functionality()

            self.system_state = "READY"
            self.setup_complete = True
            self.display_controller.show_system_status("READY")
            print("=== System Initialization Completed ===")

        except Exception as e:
            self.system_state = "ERROR"
            self.handle_initialization_error(e)

    def show_startup_animation(self):
        """Display system startup animation"""
        animation_sequence = [
            Image.HAPPY,
            Image.HEART,
            Image.YES
        ]

        for frame in animation_sequence:
            display.show(frame)
            sleep(300)

        display.scroll("FACE SYS")
        sleep(500)

    def test_basic_functionality(self):
        """Test basic system functionality"""
        try:
            # Test display with numbers 0-2
            for i in range(3):
                self.display_controller.display_number(i)
                sleep(300)

            display.clear()
            print("✓ Basic functionality test passed")

        except Exception as e:
            print(f"✗ Basic functionality test failed: {e}")
            raise

    def handle_initialization_error(self, error):
        """Handle initialization errors"""
        print(f"!!! System initialization failed: {error}")
        self.error_count += 1
        self.display_controller.show_system_status("ERROR")

    def run(self):
        """Main system operation loop"""
        if not self.setup_complete:
            print("System not initialized, cannot start")
            return

        print("=== Starting Main System Loop ===")

        cycle_count = 0
        max_cycles = 10000

        while cycle_count < max_cycles and self.system_state != "SHUTDOWN":
            try:
                cycle_count += 1

                # Process serial data
                self.process_serial_data()

                # Handle button inputs
                self.handle_button_inputs()

                # Perform recognition cycle
                if self.system_state == "READY":
                    self.perform_recognition_cycle()

                # Control loop speed
                sleep(100)

            except Exception as e:
                self.handle_runtime_error(e)

        self.cleanup_system()

    def process_serial_data(self):
        """Process incoming serial data"""
        try:
            if uart.any():
                data = uart.read().decode('utf-8').strip()
                if data:
                    print(f"Received serial data: '{data}'")
                    self.process_received_data(data)

        except Exception as e:
            print(f"Serial data processing error: {e}")

    def process_received_data(self, data):
        """Process received data"""
        try:
            # Parse number from data
            number = self.parse_data_to_number(data)
            if number is not None:
                self.handle_number_input(number)

        except Exception as e:
            print(f"Data processing error: {e}")

    def parse_data_to_number(self, data):
        """Parse number from data"""
        try:
            # Extract digits only
            clean_data = ''.join(filter(str.isdigit, data))
            if clean_data:
                return int(clean_data)
        except ValueError:
            pass
        return None

    def handle_number_input(self, number):
        """Handle number input"""
        if 0 <= number <= 99:
            self.current_number = number
            self.display_controller.display_number(number)
            self.system_state = "RECOGNIZED"
            print(f"Displaying number: {number}")
        else:
            print(f"Invalid number: {number}")
            self.display_controller.show_system_status("ERROR")

    def handle_button_inputs(self):
        """Handle button inputs"""
        if button_a.was_pressed():
            self.handle_button_a()

        if button_b.was_pressed():
            self.handle_button_b()

    def handle_button_a(self):
        """Handle button A press"""
        if self.system_state == "READY":
            self.current_number = (self.current_number + 1) % 100
            self.display_controller.display_number(self.current_number)
            print(f"Button A: Number increased to {self.current_number}")

    def handle_button_b(self):
        """Handle button B press"""
        if self.system_state == "READY":
            self.run_quick_test()
            print("Button B: Quick test executed")

    def perform_recognition_cycle(self):
        """Perform recognition cycle"""
        # Perform recognition every 100 cycles
        if self.cycle_count % 100 == 0:
            try:
                self.system_state = "PROCESSING"
                self.display_controller.show_system_status("PROCESSING")
                sleep(500)

                # Placeholder for actual recognition logic
                # recognized_id = self.recognition_system.recognize_face()
                # if recognized_id is not None:
                #     self.handle_number_input(recognized_id)

                self.system_state = "READY"
                self.display_controller.show_system_status("READY")

            except Exception as e:
                print(f"Recognition cycle error: {e}")
                self.system_state = "ERROR"

    def handle_runtime_error(self, error):
        """Handle runtime errors"""
        print(f"!!! Runtime error: {error}")
        self.error_count += 1

        if self.error_count >= 3:  # Reduced error threshold
            self.system_state = "ERROR"
            self.display_controller.show_system_status("ERROR")

        sleep(1000)

    def run_quick_test(self):
        """Run quick system test"""
        print("Running quick test...")
        self.display_controller.display_number(8)
        sleep(1000)
        display.show(Image.YES)
        sleep(500)
        display.clear()

    def cleanup_system(self):
        """Cleanup system resources"""
        print("Cleaning up system...")
        display.clear()
        print("System cleanup completed")

# Main program entry
if __name__ == "__main__":
    try:
        print("Micro:bit Face Recognition System Starting")

        # Create system instance
        face_system = MicrobitFaceSystem()

        if face_system.setup_complete:
            print("System ready, starting main loop")
            face_system.run()
        else:
            print("System initialization failed")
            display.scroll("INIT FAIL")

    except Exception as e:
        print(f"!!! System startup error: {e}")
        display.show(Image.SAD)
        display.scroll("ERROR")
        print("Please reset device and check connections")
