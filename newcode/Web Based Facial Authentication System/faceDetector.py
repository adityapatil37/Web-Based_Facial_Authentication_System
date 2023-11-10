import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection


def detect_faces(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Initialize the Face Detection module
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        # Convert the image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and get the results
        results = face_detection.process(image_rgb)

        # Get the number of detected faces
        num_faces = 0
        if results.detections:
            num_faces = len(results.detections)
            print(num_faces, " faces")

    return num_faces
