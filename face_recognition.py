# face_recognition.py
import cv2
import numpy as np
import serial
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FaceRecognitionSystem:
    """Core Face Recognition System Class"""

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.known_faces = {}
        self.face_id_counter = 1
        self.serial_connection = None
        self.setup_serial_connection()

    def setup_serial_connection(self):
        """Initialize serial connection"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.serial_connection = serial.Serial('COM3', 115200, timeout=1)
                time.sleep(2)  # Connection stabilization time
                logging.info(f"Serial connection established successfully on attempt {attempt + 1}")
                return True
            except serial.SerialException as e:
                logging.warning(f"Serial connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logging.error("Failed to establish serial connection, using fallback mode")
                time.sleep(1)
        return False

    def capture_face_image(self):
        """Capture face image"""
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            logging.error("Cannot access camera, trying alternative indices")
            for i in range(1, 4):
                camera = cv2.VideoCapture(i)
                if camera.isOpened():
                    logging.info(f"Camera found at index {i}")
                    break
            if not camera.isOpened():
                logging.error("Cannot access any camera")
                return None

        ret, frame = camera.read()
        face_region = None

        if ret:
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Face detection
            faces = self.face_cascade.detectMultiScale(
                gray_frame, 1.1, 4, minSize=(100, 100)
            )

            if len(faces) > 0:
                # Take the largest face
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                if w > 50 and h > 50:  # Minimum size check
                    face_region = gray_frame[y:y+h, x:x+w]
                    # Draw bounding box
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                else:
                    logging.info("Detected face too small, ignoring")
            else:
                logging.info("No faces detected in frame")

            # Display detection results
            cv2.imshow('Face Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("User quit")

        camera.release()
        return face_region

    def register_new_face(self, face_image):
        """Register a new face"""
        if face_image is None or face_image.size == 0:
            logging.error("Invalid face image for registration")
            return None

        # Quality check
        if face_image.shape[0] < 50 or face_image.shape[1] < 50:
            logging.warning("Face image too small for registration")
            return None

        face_id = self.face_id_counter
        self.known_faces[face_id] = face_image
        self.face_id_counter += 1
        logging.info(f"New face registered successfully, ID: {face_id}")
        return face_id

    def recognize_face(self, input_face):
        """Recognize face"""
        if len(self.known_faces) == 0:
            logging.info("No faces registered in database")
            return None

        if input_face is None or input_face.size == 0:
            logging.warning("Input face image for recognition is invalid")
            return None

        best_match_id = None
        best_similarity_score = 0
        similarity_threshold = 0.7

        for face_id, stored_face in self.known_faces.items():
            try:
                # Resize to standard dimensions
                target_size = (100, 100)
                resized_input = cv2.resize(input_face, target_size)
                resized_stored = cv2.resize(stored_face, target_size)

                # Calculate similarity
                similarity = self.calculate_similarity(resized_input, resized_stored)

                if similarity > best_similarity_score and similarity > similarity_threshold:
                    best_similarity_score = similarity
                    best_match_id = face_id

            except Exception as e:
                logging.error(f"Face comparison error: {e}")
                continue

        if best_match_id:
            logging.info(f"Recognition successful: Face ID {best_match_id}, similarity {best_similarity_score:.3f}")
        else:
            logging.info("No matching face found")

        return best_match_id

    def calculate_similarity(self, image1, image2):
        """Calculate similarity between two images"""
        try:
            result = cv2.matchTemplate(image1, image2, cv2.TM_CCOEFF_NORMED)
            return result[0][0]
        except Exception as e:
            logging.error(f"Similarity calculation error: {e}")
            return 0.0

    def send_to_microbit(self, number):
        """Send data to Micro:bit"""
        if self.serial_connection is None or not self.serial_connection.is_open:
            logging.error("Serial connection not available")
            return False

        try:
            message = f"{number}\n"
            self.serial_connection.write(message.encode('utf-8'))
            logging.info(f"Sent to Micro:bit: {number}")
            return True
        except Exception as e:
            logging.error(f"Failed to send to Micro:bit: {e}")
            return False

    def run_recognition_loop(self):
        """Run recognition loop"""
        logging.info("Face recognition system started")
        print("Press 'q' to quit, 'r' to manually register new face")

        try:
            while True:
                face = self.capture_face_image()

                if face is not None:
                    face_id = self.recognize_face(face)

                    if face_id is None:
                        logging.info("New face detected, starting registration")
                        new_id = self.register_new_face(face)
                        if new_id is not None:
                            self.send_to_microbit(new_id)
                    else:
                        self.send_to_microbit(face_id)

                time.sleep(1)  # Control processing frequency

        except KeyboardInterrupt:
            logging.info("Recognition system stopped by user")
        except Exception as e:
            logging.error(f"Error in recognition loop: {e}")
        finally:
            # Cleanup resources
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    system = FaceRecognitionSystem()
    system.run_recognition_loop()
