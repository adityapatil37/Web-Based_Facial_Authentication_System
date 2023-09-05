from flask import Flask, render_template, flash, redirect, url_for, request
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import cv2
import mediapipe as mp
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'  # MongoDB connection URL

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define the User model
class User(UserMixin):
    def __init__(self, username, password, image):
        self.username = username
        self.password = password
        self.image = image

# Define the routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        image = request.files['image']

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store the user data in MongoDB
        user = User(username=username, password=hashed_password, image=image.read())
        mongo.db.users.insert_one(user.__dict__)

        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.users.find_one({'username': username})

        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(username=username, password=user['password'], image=user['image']))
            return redirect(url_for('authenticate'))

        flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/authenticate', methods=['GET', 'POST'])
@login_required
def authenticate():
    if request.method == 'POST':
        # Capture a live image from the webcam using OpenCV
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            flash('Failed to capture live image', 'danger')
            return redirect(url_for('authenticate'))

        # Load the stored image from the database
        stored_image = np.frombuffer(current_user.image, np.uint8)
        stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR)

        # Initialize MediaPipe Face Detection
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

        # Detect faces in the live image
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

                # Perform image comparison (e.g., using template matching)
                similarity = template_matching(stored_image, live_face)

                if similarity > 0.7:  # Adjust the threshold as needed
                    flash('Authentication successful', 'success')
                else:
                    flash('Authentication failed', 'danger')

    return render_template('authenticate.html')

def template_matching(template, target):
    # Perform image comparison (template matching)
    # You can replace this with a more advanced comparison method
    # Return a similarity score (higher values indicate better match)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    _, similarity, _, _ = cv2.minMaxLoc(result)
    return similarity

if __name__ == '__main__':
    app.run(debug=True)
