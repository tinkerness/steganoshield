from flask import Flask, session, render_template, request, redirect
import pyrebase

app = Flask(__name__)
config = {
    'apiKey': "AIzaSyC4WE3WDalROurO2q9ybiPxF8FsT19ndSs",
    'authDomain': "steganoshield.firebaseapp.com",
    'projectId': "steganoshield",
    'storageBucket': "steganoshield.appspot.com",
    'messagingSenderId': "703639922932",
    'appId': "1:703639922932:web:800aa593bda8ee96a5d6a1",
    'measurementId': "G-KGBWCDXW4R",
    'databaseURL': ''
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
app.secret_key = 'secret'

def is_user_authenticated():
    if 'user' in session:
        try:
            user = auth.get_account_info(session['user']['idToken'])
            return True
        except Exception as e:
            print(f"Error verifying user: {e}")
            return False
    return False

@app.route('/')
def index():
    if is_user_authenticated():
        return render_template('dashboard.html')
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user
            return redirect('/dashboard')  # Redirect to the dashboard after successful login
        except:
            return 'Failed to login'
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if is_user_authenticated():
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user
            return redirect('/login')
        except:
            return 'Failed to signup'
    return render_template('create_user.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/decrypt')
def decrypt():
    return render_template('decrypt_message.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(port=1111)