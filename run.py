# app.py

from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import cv2
import mediapipe as mp
import numpy as np
import base64
from flask_cors import CORS
import jwt
import datetime
import face_recognition

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'  # MongoDB connection URL

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
CORS(app)


def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Define the routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():

    if 'user' in session:
        return redirect(url_for('index'))  # Redirect to the index page if the user is already authenticated

    username = request.form['username']
    raw_password = request.form['password']
    image = request.files['image']

    # Check if the username is already in use
    if mongo.db.users.find_one({'username': username}):
        return "Username is already in use."

        # Hash the password using bcrypt
    hashed_password = bcrypt.generate_password_hash(raw_password).decode('utf-8')
    user_data = {
            'username': username,
            'password': hashed_password,
            'image': image.read()
        }
        # Save user data to MongoDB with the hashed password
    mongo.db.users.insert_one(user_data)

    return redirect(url_for('login'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():

#     if 'user' in session:
#         return redirect(url_for('index'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         image = request.files['image']

#         # Check if the username already exists in the database
#         existing_user = mongo.db.users.find_one({'username': username})
#         if existing_user:
#             flash('Username already exists. Please choose a different username.', 'danger')
#             return redirect(url_for('register'))

#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

#         user_data = {
#             'username': username,
#             'password': hashed_password,
#             'image': image.read()
#         }
#         mongo.db.users.insert_one(user_data)

#         flash('Your account has been created!', 'success')
#         return redirect(url_for('login'))

#     return render_template('register.html')










# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if 'user' in session:
#         return redirect(url_for('index'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = mongo.db.users.find_one({'username': username})

#         if user and bcrypt.check_password_hash(user['password'], password):
#             session['user'] = user['username']
#             flash('Login successful', 'success')
#             return redirect(url_for('authenticate'))

#         flash('Login failed. Please check your username and password.', 'danger')

#     return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Check if the user exists in the database
    user = mongo.db.users.find_one({'username': username})

    if user and bcrypt.check_password_hash(user['password'], password):
        # Password matches, set the user in the session
        token = generate_token(username)
        return jsonify({'message': 'Login successful', 'token': token}), 200
    else:
        return jsonify({'message': 'Login failed'}), 401

# @app.route('/authenticate', methods=['GET', 'POST'])
# def authenticate():


#     if 'user' not in session:
#         return redirect(url_for('login'))

#     live_image_data = None  # Initialize to None

#     if request.method == 'POST':
#         # Set the desired resolution and frame rate
#         cap = cv2.VideoCapture(0)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Width
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Height
#         cap.set(cv2.CAP_PROP_FPS, 30)  # Frame rate (adjust as needed)

#         ret, frame = cap.read()
#         cap.release()

#         if not ret:
#             flash('Failed to capture live image', 'danger')
#             return redirect(url_for('authenticate'))

#         # Retrieve the stored image from MongoDB for the authenticated user
#         username = session['user']
#         user = mongo.db.users.find_one({'username': username})

#         if not user:
#             flash('User not found', 'danger')
#             return redirect(url_for('authenticate'))

#         stored_image_binary = user['image']

#         # Convert the binary image data to a NumPy array
#         stored_image = np.frombuffer(stored_image_binary, np.uint8)
#         stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR) #known face encoding image1 in numpy arrey

#         # Initialize MediaPipe Face Detection
#         mp_face_detection = mp.solutions.face_detection
#         face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

#         # Detect faces in the live image and perform template matching
#         with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
#             live_image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = face_detection.process(live_image_rgb)

#         if results.detections:
#             for detection in results.detections:
#                 bboxC = detection.location_data.relative_bounding_box
#                 ih, iw, _ = frame.shape
#                 x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
#                              int(bboxC.width * iw), int(bboxC.height * ih)

#                 # Extract the face region from the live image
#                 live_face = frame[y:y + h, x:x + w]
#                 np_live_image = np.array(live_image_rgb)
#                 print(np_live_image)

#                 # live_face_encoding= face_recognition.face_encodings(np_live_image)[0]

#                 live_face_encodings = face_recognition.face_encodings(np_live_image)

#                 if live_face_encodings:
#                     live_face_encoding = live_face_encodings[0]
#                     # Rest of your code for authentication
#                 else:
#                     flash('No face found in the live image', 'danger')
#                     # Handle the case where no face is detected in the live image


#                 stored_face_encoding_db= face_recognition.face_encodings(stored_image)[0]
                

#                 # Perform image comparison (template matching)
#                 similarity = face_recognition.compare_faces([live_face_encoding], stored_face_encoding_db)

#                 if similarity[0]:  # no adjustment
#                     flash('Authentication successful', 'success')
#                 else:
#                     flash('Authentication failed', 'danger')

#                 # Draw a rectangle around the detected face
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle

#         # Convert the annotated live image to base64 format for displaying in HTML
#         _, buffer = cv2.imencode('.jpg', frame)
#         live_image_data = base64.b64encode(buffer).decode()

#     return render_template('authenticate.html', live_image=f'data:image/jpeg;base64,{live_image_data}')



@app.route('/authentication', methods=['POST'])
def authentication():

    # Get the image file from the request
    image_file = request.files.get('image')

    if image_file is None:
        return jsonify({'message': 'No image provided'}), 400

    # Convert the image to a NumPy array
    image_data = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # Perform face recognition on the captured image
    captured_face_encodings = face_recognition.face_encodings(image)
    
    if not captured_face_encodings:
        return jsonify({'message': 'No face found in the captured image'}), 400

    captured_face_encoding = captured_face_encodings[0]


    username = session['user']
    user = mongo.db.users.find_one({'username': username})

    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('authenticate'))

    stored_image_binary = user['image']

    # Convert the binary image data to a NumPy array
    stored_image = np.frombuffer(stored_image_binary, np.uint8)
    stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR)

    stored_face_encoding_db= face_recognition.face_encodings(stored_image)[0]


    # Compare the captured face encoding with the known face encoding
    results = face_recognition.compare_faces([stored_face_encoding_db], captured_face_encoding)

    if results[0]:
        return jsonify({'message': 'Authentication successful'})
    else:
        return jsonify({'message': 'Authentication failed'}), 401


    # if 'username' not in session:
    #     return redirect(url_for('login'))
    
    # username = session['username']
    # user = mongo.db.users.find_one({'username': username})
    
    # if user:
    #     user_image_base64 = base64.b64encode(user['user_image']).decode('utf-8')
    #     user_data = {
    #         'fullname' : user['username'],
    #         'user_name' : user_image_base64
    #     }
    #     return jsonify({user_data}), 200
    # else:
    #     return jsonify({'message': 'User not found'}), 404
    
# 'user_image': base64.b64encode(user['image']).decode('utf-8')


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











@app.route('/admin', methods=['GET'])
def admin():
    if 'username' in session:
        username = session['username']
        user = mongo.db.users.find_one({'username': username})

        if user and user.get('is_admin', False):
            # Fetch all user data from the database
            users = list(mongo.db.users.find({}, {'_id': 0}))

            return jsonify({'users': users})
        else:
            return jsonify({'message': 'Unauthorized access to the admin page'}, 403)
    else:
        return jsonify({'message': 'Not logged in'}, 401)






@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
