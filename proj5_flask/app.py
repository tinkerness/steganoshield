from flask import Flask, render_template, request, redirect, url_for
import steganoshield

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if steganoshield.login(username, password):
            return redirect(url_for('index'))
        else:
            return "Invalid username or password!"
    return render_template('login.html')

# Add similar routes for create_user, encrypt_message, and decrypt_message
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if steganoshield.create_user(username, password):
            return redirect(url_for('index'))
        else:
            return "Failed to create user!"
    return render_template('create_user.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        cover_image = request.files['cover_image']
        if steganoshield.encrypt_message(username, message, cover_image):
            return redirect(url_for('index'))
        else:
            return "Failed to encrypt message!"
    return render_template('encrypt_message.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     encrypted_image = request.files['encrypted_image']
    #     decrypted_message = steganoshield.decrypt_message(username, encrypted_image)
    #     if decrypted_message:
    #         return decrypted_message
    #     else:
    #         return "Failed to decrypt message!"
    return render_template('decrypt_message.html')


@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/')
@app.route('/login')
@app.route('/signup')
@app.route('/dashboard')
@app.route('/encrypt')
@app.route('/decrypt')
@app.route('/notifications')
@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

if __name__ == '__main__':
    app.run(debug=True)