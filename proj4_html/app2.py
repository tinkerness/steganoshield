from flask import Flask, flash, session, render_template, request, redirect
import pyrebase
from werkzeug.utils import secure_filename
import os
import firebase_admin
from firebase_admin import credentials, storage
from steganoCopy import create_user, loginUser, save_user_data, load_user_data, encrypt_message, hide_message_in_image, extract_and_decrypt_message
import time
from io import BytesIO
from PIL import Image

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

cred = credentials.Certificate('config/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'steganoshield.appspot.com'
})

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
                print("Logged in as user:", username)
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
@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if is_user_authenticated():
        if request.method == 'POST':
            stego_image = request.files.get('stego_image')
            if stego_image:
                stego_image_filename = secure_filename(stego_image.filename)
                stego_image_path = os.path.join(app.config['UPLOAD_FOLDER'], stego_image_filename)
                stego_image.save(stego_image_path)

                user_data = db.child("users").child(session['user']['localId']).get().val()
                username = user_data['username']
                private_key = load_user_data()[username]['private_key']

                try:
                    decrypted_message = extract_and_decrypt_message(stego_image_path, private_key, username)
                    return render_template('decrypt_message.html', decrypted_message=decrypted_message)
                except Exception as e:
                    print(f"Error decrypting message: {e}")
                    return render_template('decrypt_message.html', error_message="Failed to decrypt the message.")
        return render_template('decrypt_message.html')
    else:
        return redirect('/login')
# Assuming Firebase Admin SDK is already initialized
def get_storage_bucket():
    # Returns the Firebase Storage bucket
    return storage.bucket()

def get_cover_image_blob(filename):
    # Secure the filename to prevent path traversal or invalid characters
    secure_name = secure_filename(filename)
    # Define the path in Firebase Storage for cover images
    path = f"uploads/{secure_name}"
    # Create a blob for this path
    bucket = get_storage_bucket()
    return bucket.blob(path)

def get_stego_image_blob(filename):
    # Secure the filename
    secure_name = secure_filename(filename)
    # Define the path in Firebase Storage for stego images
    path = f"stego_images/{secure_name}"
    # Create a blob for this path
    bucket = get_storage_bucket()
    return bucket.blob(path)

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

# Set the stego folder for stego images
app.config['STEGO_FOLDER'] = 'stego_images'
os.makedirs(app.config['STEGO_FOLDER'], exist_ok=True)

# -----------dashboard---------------

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
                print('Recipient:', recipient)
                print('Message:', message)
                cover_image_filename = secure_filename(cover_image.filename)
                # cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_image_filename)
                # cover_image.save(cover_image_path)
                # print('Cover image saved successfully in device path: ',cover_image_path,'!')

                # # Reset file stream to beginning
                # cover_image.seek(0)
                # # Get a blob for the cover image in the 'uploads' folder
                cover_image_blob = get_cover_image_blob(cover_image_filename)
                cover_image_blob.upload_from_file(cover_image)  # Upload the cover image
                # Optionally make it publicly accessible
                cover_image_blob.make_public()
                # Get the public URL of the uploaded cover image
                cover_image_url = cover_image_blob.public_url
                print('Cover image uploaded to Firebase Storage at:',cover_image_url,'!')

                
                result = db.child("users").order_by_child("username").equal_to(recipient).get()
                if not result.val():
                    print('Recipient not found in Firestore!')
    
                recipient_user_data = list(result.val().values())[0]
                recipient_id = list(result.val().keys())[0]  # Get the user ID (document key)
                recipient_public_key = recipient_user_data.get('public_key')
                # print('public key of receiver: ', recipient_public_key, '\nrecipient_id : ', recipient_id)
                if not recipient_public_key:
                    print('Recipient public key not found!')
                
                # user_data = load_user_data()
                # sender_private_key = user_data[username]['private_key']

                encrypted_message = encrypt_message(message, recipient_public_key)
                print("encrypted_message : ",encrypted_message)

                # Create the stego image with the cover image and encrypted message
                cover_image.seek(0)  # Ensure we're at the beginning
                cover_image_pil = Image.open(cover_image)  # Open the image with PIL
                stego_image = hide_message_in_image(encrypted_message, cover_image_pil)

                
                # Save the stego image to a byte stream
                stego_image_stream = BytesIO()  # In-memory byte stream
                stego_image.save(stego_image_stream, format="PNG")  # Save the PIL image to the stream
                stego_image_stream.seek(0)  # Reset stream to beginning

                # Get a blob for the stego image in the 'stego_images' folder
                stego_image_blob = get_stego_image_blob(f"{username}_to_{recipient}_stego.png")

                # Upload the stego image from the byte stream
                stego_image_blob.upload_from_file(stego_image_stream)
                
                stego_image_blob.make_public()
                stego_image_url = stego_image_blob.public_url


                # stego_image_filename = f"{username}_to_{recipient}_stego.png"
                # # print('cover_image_path : ',cover_image_path, 'stego_image_filename : ',stego_image_filename)
                # stego_image = hide_message_in_image(encrypted_message, cover_image_path)
                # # stego_image = hide_message_in_image(encrypted_message, cover_image_url)
                # # Get a blob for the stego image in the 'stego_images' folder
                # stego_image_blob = get_stego_image_blob(stego_image_filename)
                # stego_image_blob.upload_from_file(stego_image)  # Upload the stego image

                # # Optionally make the stego image publicly accessible
                # stego_image_blob.make_public()

                # # Use the public URL of the stego image to reference it in notifications
                # stego_image_url = stego_image_blob.public_url
                print('Stego image uploaded to Firebase Storage at:',stego_image_url,'!')


                # # stego_image_path = os.path.join('stego_images', stego_image_filename)
                # stego_image_path = os.path.join(app.config['STEGO_FOLDER'], stego_image_filename)
                # stego_image.save(stego_image_path)
                # print('stego image saved successfully in path: ',stego_image_path,'!')

                # Store the steganographic image path in the recipient's notifications
                notification_data = {
                    'sender_id': sender_id,
                    'sender_username': username,
                    'message': message,
                    'stego_image_path': stego_image_url,
                    'timestamp': time.time()  # Current time in seconds since epoch
                }
                print('notification_data : ',notification_data)
                db.child("notifications").child(recipient_id).push(notification_data)
                return 'Message encrypted and hidden in the image successfully!'

        return render_template('dashboard.html', username=username)
    else:
        return redirect('/login')
    
# # ------------decrypt----------------
# @app.route('/decrypt')
# def decrypt():
#     if is_user_authenticated():
#         user_data = db.child("users").child(session['user']['localId']).get().val()
#         username = user_data['username']
#         private_key = user_data['private_key']
#         # print('receiver: ', username , ', private key: ', private_key)

#         if request.method == 'POST':
#             stego_image = request.files.get('cover_image')

#             if stego_image:
#                 print('Received stego_image')
#                 stego_image_filename = secure_filename(stego_image.filename)
#                 stego_image_path = os.path.join(app.config['STEGO_FOLDER'], stego_image_filename)
#                 stego_image.save(stego_image_path)
#                 print('Stego image saved successfully in path: ',stego_image_path,'!')

#                 decrypted_message = extract_and_decrypt_message(stego_image_path, private_key, username)
#                 print('Decrypted message:', decrypted_message)
#                 return 'Message decrypted successfully!'
#         # # Check if a file was uploaded
#         # if 'cover_image' in request.files:
#         #     file = request.files['cover_image']
#         #     filename = secure_filename(file.filename)
#         #     file.save(filename)

#         #     try:
#         #         # Now you can call the extract_and_decrypt_message() function
#         #         message = extract_and_decrypt_message(filename)
#         #         # Do something with the decrypted message...
#         #         return 'Message decrypted'
#         #     except Exception as e:
#         #         # If an error occurred, return an error message
#         #         return 'An error occurred: ' + str(e)
#         # print('No file uploaded')

#     return render_template('decrypt_message.html')

if __name__ == '__main__':
    app.run(port=1111)