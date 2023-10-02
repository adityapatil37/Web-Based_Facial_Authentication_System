# app.py

from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import cv2
import mediapipe as mp
import numpy as np
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'  # MongoDB connection URL

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Define the routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # if 'user' in session:
    #     return redirect(url_for('index'))

    # if request.method == 'POST':
    #     username = request.form.get('username')
    #     password = request.form.get('password')
    #     image = request.files['image']

    #     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    #     user_data = {
    #         'username': username,
    #         'password': hashed_password,
    #         'image': image.read()
    #     }
    #     mongo.db.users.insert_one(user_data)

    #     flash('Your account has been created!', 'success')
    #     return redirect(url_for('login'))

    # return render_template('register.html')




    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        image = request.files['image']

        # Check if the username already exists in the database
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            'username': username,
            'password': hashed_password,
            'image': image.read()
        }
        mongo.db.users.insert_one(user_data)

        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.users.find_one({'username': username})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = user['username']
            flash('Login successful', 'success')
            return redirect(url_for('authenticate'))

        flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():

    # if 'user' not in session:
    #     return redirect(url_for('login'))

    # live_image_data = None  # Initialize to None

    # if request.method == 'POST':
    #     # Capture a live image from the webcam using OpenCV
    #     cap = cv2.VideoCapture(0)
    #     ret, frame = cap.read()
    #     cap.release()

    #     if not ret:
    #         flash('Failed to capture live image', 'danger')
    #         return redirect(url_for('authenticate'))

    #     # Retrieve the stored image from MongoDB for the authenticated user
    #     username = session['user']
    #     user = mongo.db.users.find_one({'username': username})

    #     if not user:
    #         flash('User not found', 'danger')
    #         return redirect(url_for('authenticate'))

    #     stored_image_binary = user['image']

    #     # Convert the binary image data to a NumPy array
    #     stored_image = np.frombuffer(stored_image_binary, np.uint8)
    #     stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR)

    #     # Initialize MediaPipe Face Detection
    #     mp_face_detection = mp.solutions.face_detection
    #     face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    #     # Detect faces in the live image and perform template matching
    #     with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
    #         live_image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         results = face_detection.process(live_image_rgb)

    #     if results.detections:
    #         for detection in results.detections:
    #             bboxC = detection.location_data.relative_bounding_box
    #             ih, iw, _ = frame.shape
    #             x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
    #                          int(bboxC.width * iw), int(bboxC.height * ih)

    #             # Extract the face region from the live image
    #             live_face = frame[y:y + h, x:x + w]

    #             # Perform image comparison (template matching)
    #             similarity = template_matching(stored_image, live_face)

    #             if similarity > 0.7:  # Adjust the threshold as needed
    #                 flash('Authentication successful', 'success')
    #             else:
    #                 flash('Authentication failed', 'danger')

    #             # Draw a rectangle around the detected face
    #             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle

    #     # Convert the annotated live image to base64 format for displaying in HTML
    #     _, buffer = cv2.imencode('.jpg', frame)
    #     live_image_data = base64.b64encode(buffer).decode()

    # return render_template('authenticate.html', live_image=f'data:image/jpeg;base64,{live_image_data}')




    if 'user' not in session:
        return redirect(url_for('login'))

    live_image_data = None  # Initialize to None

    if request.method == 'POST':
        # Set the desired resolution and frame rate
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Width
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Height
        cap.set(cv2.CAP_PROP_FPS, 30)  # Frame rate (adjust as needed)

        ret, frame = cap.read()
        cap.release()

        if not ret:
            flash('Failed to capture live image', 'danger')
            return redirect(url_for('authenticate'))

        # Retrieve the stored image from MongoDB for the authenticated user
        username = session['user']
        user = mongo.db.users.find_one({'username': username})

        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('authenticate'))

        stored_image_binary = user['image']

        # Convert the binary image data to a NumPy array
        stored_image = np.frombuffer(stored_image_binary, np.uint8)
        stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR)

        # Initialize MediaPipe Face Detection
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

        # Detect faces in the live image and perform template matching
        with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
            live_image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(live_image_rgb)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                             int(bboxC.width * iw), int(bboxC.height * ih)

                # Extract the face region from the live image
                live_face = frame[y:y + h, x:x + w]

                # Perform image comparison (template matching)
                similarity = template_matching(stored_image, live_face)

                if similarity > 0.7:  # Adjust the threshold as needed
                    flash('Authentication successful', 'success')
                else:
                    flash('Authentication failed', 'danger')

                # Draw a rectangle around the detected face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle

        # Convert the annotated live image to base64 format for displaying in HTML
        _, buffer = cv2.imencode('.jpg', frame)
        live_image_data = base64.b64encode(buffer).decode()

    return render_template('authenticate.html', live_image=f'data:image/jpeg;base64,{live_image_data}')

# Template Matching Function
def template_matching(template, target):
    # Convert the target and template images to grayscale
    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Find the location of the best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # You can adjust the threshold as needed (higher values are more strict)
    threshold = 0.7

    if max_val >= threshold:
        return max_val
    else:
        return 0.0








@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
