from flask import Flask, session, render_template, request, redirect
import pyrebase
from werkzeug.utils import secure_filename
import os

from steganoCopy import create_user, loginUser, save_user_data, load_user_data, encrypt_message, hide_message_in_image


app = Flask(__name__)
config = {
    'apiKey': "AIzaSyC4WE3WDalROurO2q9ybiPxF8FsT19ndSs",
    'authDomain': "steganoshield.firebaseapp.com",
    'projectId': "steganoshield",
    'storageBucket': "steganoshield.appspot.com",
    'messagingSenderId': "703639922932",
    'appId': "1:703639922932:web:800aa593bda8ee96a5d6a1",
    'measurementId': "G-KGBWCDXW4R",
    'databaseURL': 'https://steganoshield-default-rtdb.firebaseio.com/'
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()  # Initialize the Firestore database
app.secret_key = 'secret'

def is_user_authenticated():
    if 'user' in session:
        try:
            user_id_token = session['user']['idToken']
            auth.get_account_info(user_id_token)
            return True
        except Exception as e:
            print(f"Error verifying user: {e}")
            return False
    return False

# -----------index-------------------
@app.route('/')
def index():
    if is_user_authenticated():
        return redirect('/dashboard')
    return render_template('index.html')


# --------login---------------
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user
            
            # Check if the login function returns True
            is_login_successful = loginUser(username, password)
            if is_login_successful:
                return redirect('/dashboard')
            else:
                return 'Failed to to login'
        except  Exception as e:
            print(e)
            return 'Failed to login'
    return render_template('login.html')


# -----------Signup--------------
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if is_user_authenticated():
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user
            db.child("users").child(user['localId']).set({
                'username': username,
                'email': email
            })
            create_user(username, password)
            user_data = load_user_data()
            public_key = user_data[username]['public_key']
            db.child("users").child(user['localId']).child('public_key').set(public_key)
            return redirect('/login')
        except Exception as e:
            print(f"Error signing up user: {e}")
            return 'Failed to signup'
    return render_template('create_user.html')


# -----------logout-----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ------------decrypt----------------
@app.route('/decrypt')
def decrypt():
    return render_template('decrypt_message.html')

# -----------notifications------------
@app.route('/notifications')
def notifications():
    if is_user_authenticated():
        try:
            # Retrieve user data
            user_data = db.child("users").child(session['user']['localId']).get().val()
            if user_data:
                username = user_data['username']
                user_id = session['user']['localId']

                # Retrieve notifications for the user
                notifications_dict = db.child("notifications").child(user_id).get().val() or {}
                notifications_list = []

                # Convert the dictionary to a list of dictionaries
                for notification_id, notification_data in notifications_dict.items():
                    notifications_list.append(notification_data)

                return render_template('notifications.html', username=username, notifications=notifications_list)
            else:
                # Handle case where user data is not found
                return render_template('error.html', message="User data not found.")
        except Exception as e:
            print(f"Error retrieving user data or notifications: {e}")
            return render_template('error.html', message="An error occurred. Please try again later.")
    else:
        return redirect('/login')

# Set the upload folder for cover images
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -----------dashboard---------------

# @app.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     if is_user_authenticated():
#         # Retrieve the user's username or email from the session or the Firestore database
#         user_data = db.child("users").child(session['user']['localId']).get().val()
#         username = user_data['username']

#         if request.method == 'POST':
#             recipient = request.form.get('recipient')
#             message = request.form.get('message')
#             cover_image = request.files.get('cover_image')

#             if recipient and message and cover_image:
#                 # Save the cover image
#                 cover_image_filename = secure_filename(cover_image.filename)
#                 cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_image_filename)
#                 cover_image.save(cover_image_path)

#                 # Get the recipient's public key from Firebase Realtime Database
#                 recipient_public_key = db.child("users").order_by_child("username").equal_to(recipient).get().val()
#                 if recipient_public_key:
#                     recipient_public_key = list(recipient_public_key.values())[0]['public_key']
#                 else:
#                     return 'Recipient not found!'

#                 # Get the sender's private key from users.json
#                 user_data = load_user_data()
#                 sender_private_key = user_data[username]['private_key']

#                 # Encrypt the message
#                 encrypted_message = encrypt_message(message, recipient_public_key)

#                 # Hide the encrypted message in the cover image
#                 stego_image_filename = f"{username}_to_{recipient}_stego.png"
#                 stego_image_path = os.path.join(app.config['UPLOAD_FOLDER'], stego_image_filename)
#                 hide_message_in_image(encrypted_message, cover_image_path, stego_image_path)

#                 return 'Message encrypted and hidden in the image successfully!'

#         return render_template('dashboard.html', username=username)
#     else:
#         return redirect('/login')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if is_user_authenticated():
        user_data = db.child("users").child(session['user']['localId']).get().val()
        username = user_data['username']
        sender_id = session['user']['localId']  # Get the sender's user ID

        if request.method == 'POST':
            recipient = request.form.get('recipient')
            message = request.form.get('message')
            cover_image = request.files.get('cover_image')

            if recipient and message and cover_image:
                cover_image_filename = secure_filename(cover_image.filename)
                cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_image_filename)
                cover_image.save(cover_image_path)

                recipient_public_key = db.child("users").order_by_child("username").equal_to(recipient).get().val()
                if recipient_public_key:
                    recipient_public_key = list(recipient_public_key.values())[0]['public_key']
                    recipient_id = list(recipient_public_key.keys())[0]  # Get the recipient's user ID
                else:
                    return 'Recipient not found!'

                user_data = load_user_data()
                sender_private_key = user_data[username]['private_key']

                encrypted_message = encrypt_message(message, recipient_public_key)

                stego_image_filename = f"{username}_to_{recipient}_stego.png"
                stego_image_path = os.path.join('stego_images', stego_image_filename)
                hide_message_in_image(encrypted_message, cover_image_path, stego_image_path)

                # Store the steganographic image path in the recipient's notifications
                notification_data = {
                    'sender_id': sender_id,
                    'sender_username': username,
                    'message': message,
                    'stego_image_path': stego_image_path
                }
                db.child("notifications").child(recipient_id).push(notification_data)

                return 'Message encrypted and hidden in the image successfully!'

        return render_template('dashboard.html', username=username)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(port=1111)