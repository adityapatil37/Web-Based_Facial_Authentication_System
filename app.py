from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import numpy as np
import cv2
import base64
import checker
import tracker
import tensorflow as tf
import matplotlib.pyplot as plt
import face_recognition
import io, os
from PIL import Image
from PIL import Image
from io import BytesIO
import mediapipe as mp
import faceDetector
import ssl


app = Flask(__name__, static_url_path='/static')
# Create an SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

# Load the SSL certificate and key into the context
context.load_cert_chain('yourapp.crt', 'yourapp.key')

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'  # MongoDB connection URL

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


@app.route('/')
def first():
    return render_template('index.html')  #    <script src="../static/scripts.js"></script>

@app.route('/signup_form', methods=['POST','GET'])
def signup_form():
    return render_template('signup.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    data=request.form
    #print("the data is ",data)
    if data['password1']==data['password2']:
        existing_user = mongo.db.users.find_one({'username': data['userName']})
        if existing_user:
            return render_template('signup.html', status="This username already exists")
        elif 'image' in request.files:
            image=request.files['image']

            hashed_password = bcrypt.generate_password_hash(data['password1']).decode('utf-8') #hash password into base64

            user_data = {
                'username': data['userName'],
                'password': hashed_password,
                'image': image.read()
            }
            mongo.db.users.insert_one(user_data)
            return render_template('signup.html', status="Registration sucessfull")
        else:
            return render_template('signup.html', status="Upload your image ")
    else :
        return render_template('signup.html', status="Passwords dosen't match")

    return render_template('signup.html')

@app.route('/login_form', methods=['GET','POST'])
def login_form():

    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    data=request.form
    username=data['userName']
    user = mongo.db.users.find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        session['username']=username
        return render_template('capture.html')
    else:
        return render_template('login.html', status="Wrong Password")
    

@app.route('/verify', methods=['POST', 'GET'])
def Verification():

    if 'photo' in request.files:

        image2=request.files['photo']
        image_data = image2.read()

        file_path = 'webImage.png'
        with open(file_path, 'wb') as file:
            file.write(image_data)
        
        faces=faceDetector.detect_faces(file_path)
        
        if faces==1:

            print("only one face ")

            if 'username' in session:  

                username = session['username']
                user = mongo.db.users.find_one({'username': username})
                binaryImage = user['image']
                stored_image = np.frombuffer(binaryImage, np.uint8)
                stored_image = cv2.imdecode(stored_image, cv2.IMREAD_COLOR) #known face encoding image1 in numpy arrey
                stored_face_encoding_db= face_recognition.face_encodings(stored_image)[0]

                unknown_face_image = face_recognition.load_image_file("webImage.png")
                try:
                    unknown_face_encoding = face_recognition.face_encodings(unknown_face_image)[0]
                except IndexError or ssl.SSLEOFError:
                    return jsonify({'message':'please align your face properly'}), 404

                results = face_recognition.compare_faces([stored_face_encoding_db], unknown_face_encoding)

                if results[0]:
                    print("Person 1's face matches the unknown face.")
                    return jsonify({'user':username, 'status':200}), 200
                else:
                    return jsonify({'message':'Face does not match, Try again'}), 401



                print("this is working")


            else:
                print("error in session")
                return "Bad Request"
        elif faces==0:
            print(faces, "no face")
            return jsonify({'message':'No face Found'}), 401
        else:
            print(faces, "Multiple faces")
            return jsonify({'message':'Multiple faces Found'}), 401

    else:
        print("failed to uploading the image")
        return jsonify({'message':'Some error in uploading the image, please make sure that your authorizing camera properly '}), 401
    
@app.route('/dashboard')
def dash():
    if 'username' in session:
        username=session['username']
        return render_template('dashboard.html', user=username)
    else:
        return "Wrong Method"


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username', None)
        return render_template('index.html'), 200
    else:
        return "Login First"




if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context=context)