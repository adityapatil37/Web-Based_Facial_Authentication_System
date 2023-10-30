import mediapipe as mp
import cv2
import base64
import numpy as np
from PIL import Image
import io

# Initialize the MediaPipe Face Detection model
mp_face_detection = mp.solutions.face_detection

# Decode the base64-encoded image data into a NumPy array
def decode_image(base64_data):
    image_data = base64.b64decode(base64_data)
    image_np = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image


def detect_faces(image_data):
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    
    # Decode the image from bytes
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), -1)
    
    # Convert the image to RGB format
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(image)
        if results.detections:
            return len(results.detections)
        else:
            return 0


