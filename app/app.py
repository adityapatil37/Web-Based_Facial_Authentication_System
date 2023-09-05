# app.py

from flask import Flask

app = Flask(__name__)

# Define your routes and other app configurations here

# Example: Define a simple route
@app.route('/')
def home():
    return 'Hello, World!'

# You can add more routes and configurations as needed

if __name__ == "__main__":
    app.run(debug=True)