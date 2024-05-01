import pyrebase

config = {
    'apiKey': "AIzaSyC4WE3WDalROurO2q9ybiPxF8FsT19ndSs",
    'authDomain': "steganoshield.firebaseapp.com",
    'projectId': "steganoshield",
    'storageBucket': "steganoshield.appspot.com",
    'messagingSenderId': "703639922932",
    'appId': "1:703639922932:web:800aa593bda8ee96a5d6a1",
    'measurementId': "G-KGBWCDXW4R",
    'databaseURL' : ''
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email = 'test@gmail.com'
password = '123456'

user = auth.create_user_with_email_and_password(email, password)
print(user)