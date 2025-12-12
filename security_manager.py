# security_manager.py
import hashlib
import os
import json
from datetime import datetime
import logging

class DataSecurityManager:
    """Data Security Manager"""

    def __init__(self, storage_directory="face_data"):
        self.storage_directory = storage_directory
        self.initialize_storage()
        logging.info(f"Data Security Manager initialized, storage path: {storage_directory}")

    def initialize_storage(self):
        """Initialize storage directory"""
        try:
            if not os.path.exists(self.storage_directory):
                os.makedirs(self.storage_directory, exist_ok=True)
                logging.info(f"Created storage directory: {self.storage_directory}")

            # Verify directory is writable
            test_file = os.path.join(self.storage_directory, "write_test.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            logging.info("Storage directory is accessible and writable")

        except Exception as e:
            logging.error(f"Storage directory initialization failed: {e}")
            raise

    def hash_face_data(self, face_image):
        """Generate hash value for face data"""
        if face_image is None or face_image.size == 0:
            raise ValueError("Invalid face image provided for hashing")

        try:
            if face_image.nbytes == 0:
                raise ValueError("Face image contains no data")

            image_data = face_image.tobytes()
            hash_obj = hashlib.sha256(image_data)
            hash_value = hash_obj.hexdigest()

            logging.debug(f"Generated face data hash: {hash_value[:16]}")
            return hash_value

        except Exception as e:
            logging.error(f"Face data hashing failed: {e}")
            raise

    def secure_store_face(self, face_image, face_id):
        """Securely store face data"""
        if not isinstance(face_id, int) or face_id <= 0:
            raise ValueError(f"Invalid face ID: {face_id}")

        file_path = ""
        try:
            # Generate hash
            face_hash = self.hash_face_data(face_image)

            # Create metadata
            metadata = {
                'face_id': face_id,
                'hash_value': face_hash,
                'timestamp': datetime.now().isoformat(),
                'storage_format': 'hashed_sha256',
                'image_dimensions': face_image.shape,
                'image_size_bytes': face_image.nbytes,
                'version': '1.0'
            }

            # Validate metadata
            self.validate_metadata(metadata)

            # Create secure filename
            filename = f"face_{face_id:04d}_{face_hash[:16]}.json"
            file_path = os.path.join(self.storage_directory, filename)

            # Atomic write operation
            temp_path = file_path + '.tmp'
            with open(temp_path, 'w') as f:
                json.dump(metadata, f, indent=2, sort_keys=True)

            os.replace(temp_path, file_path)

            logging.info(f"Face data securely stored: {filename}")
            return face_hash

        except Exception as e:
            # Clean up temporary file
            temp_path = file_path + '.tmp'
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logging.error(f"Secure face data storage failed: {e}")
            raise

    def validate_metadata(self, metadata):
        """Validate metadata"""
        required_fields = ['face_id', 'hash_value', 'timestamp', 'storage_format']
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(metadata['face_id'], int):
            raise ValueError("face_id must be an integer")

        if not isinstance(metadata['hash_value'], str) or len(metadata['hash_value']) != 64:
            raise ValueError("Invalid hash value format")

    def verify_face_integrity(self, stored_hash, current_face):
        """Verify face integrity"""
        try:
            current_hash = self.hash_face_data(current_face)

            # Constant-time comparison for timing attack protection
            if len(stored_hash) != len(current_hash):
                return False

            result = 0
            for char1, char2 in zip(stored_hash, current_hash):
                result |= ord(char1) ^ ord(char2)

            is_match = (result == 0)
            logging.debug(f"Face integrity verification: {'PASS' if is_match else 'FAIL'}")
            return is_match

        except Exception as e:
            logging.error(f"Face integrity verification failed: {e}")
            return False

    def get_face_metadata(self, face_id):
        """Retrieve face metadata"""
        if not isinstance(face_id, int) or face_id <= 0:
            raise ValueError(f"Invalid face ID: {face_id}")

        try:
            matching_files = []
            for filename in os.listdir(self.storage_directory):
                if filename.startswith(f"face_{face_id:04d}_") and filename.endswith('.json'):
                    matching_files.append(filename)

            if not matching_files:
                logging.warning(f"No metadata found for face ID: {face_id}")
                return None

            # Use the most recent file
            matching_files.sort()
            filename = matching_files[-1]
            file_path = os.path.join(self.storage_directory, filename)

            with open(file_path, 'r') as f:
                metadata = json.load(f)

            self.validate_metadata(metadata)
            logging.debug(f"Retrieved metadata for face ID: {face_id}")
            return metadata

        except Exception as e:
            logging.error(f"Failed to retrieve face metadata: {e}")
            return None

class SecureFaceRecognitionSystem:
    """Secure Face Recognition System"""

    def __init__(self):
        try:
            from face_recognition import FaceRecognitionSystem
            self.recognition_system = FaceRecognitionSystem()
            self.security_manager = DataSecurityManager()
            self.face_hashes = {}
            logging.info("Secure face recognition system initialized successfully")
        except Exception as e:
            logging.error(f"Secure face recognition system initialization failed: {e}")
            raise

    def register_face_securely(self, face_image):
        """Securely register face"""
        try:
            face_id = self.recognition_system.face_id_counter
            hash_value = self.security_manager.secure_store_face(face_image, face_id)
            self.face_hashes[face_id] = hash_value
            self.recognition_system.face_id_counter += 1
            logging.info(f"New face securely registered, ID: {face_id}")
            return face_id
        except Exception as e:
            logging.error(f"Secure face registration failed: {e}")
            raise

    def recognize_face_securely(self, input_face):
        """Securely recognize face"""
        if len(self.face_hashes) == 0:
            logging.info("Secure database is empty")
            return None

        best_match_id = None
        best_confidence = 0.0
        confidence_threshold = 0.8

        try:
            for face_id, stored_hash in self.face_hashes.items():
                if self.security_manager.verify_face_integrity(stored_hash, input_face):
                    confidence = 1.0
                else:
                    confidence = 0.0

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match_id = face_id

            if best_confidence >= confidence_threshold:
                logging.info(f"Secure recognition: Face ID {best_match_id}, confidence {best_confidence:.3f}")
                return best_match_id
            else:
                logging.info(f"No secure match found (best confidence: {best_confidence:.3f})")
                return None

        except Exception as e:
            logging.error(f"Secure face recognition failed: {e}")
            return None

if __name__ == "__main__":
    # Test code
    security_mgr = DataSecurityManager()
    print("Data Security Manager test completed")
