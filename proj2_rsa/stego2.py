from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import getpass
import json

# Function to load user data from a JSON file
def load_user_data():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save user data to a JSON file
def save_user_data(data):
    with open("users.json", "w") as file:
        json.dump(data, file)

# Function to create a new user
def create_user():
    username = input("Enter a username: ")
    password = getpass.getpass("Enter a password: ")

    user_data = load_user_data()
    if username in user_data:
        print("User already exists!")
        return

    user_data[username] = {"password": password}
    save_user_data(user_data)
    print("User created successfully!")

# Function to login
def login():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    user_data = load_user_data()
    if username not in user_data or user_data[username]["password"] != password:
        print("Invalid username or password!")
        return None

    print("Login successful!")
    return username

# Function to generate RSA key pair for a user
def generate_key_pair(username):
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    user_data = load_user_data()
    user_data[username]["private_key"] = private_key.decode()
    user_data[username]["public_key"] = public_key.decode()
    save_user_data(user_data)

    print("RSA key pair generated successfully!")

# Function to encrypt a message
def encrypt_message(message, recipient_public_key):
    cipher = PKCS1_OAEP.new(RSA.import_key(recipient_public_key))
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

# Function to decrypt a message
def decrypt_message(encrypted_message, private_key):
    cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
    decrypted_message = cipher.decrypt(encrypted_message).decode()
    return decrypted_message

# Function to save encrypted message to a file
def save_encrypted_message_to_file(filename, encrypted_message):
    with open(filename, "wb") as file:
        file.write(encrypted_message)

# Function to read encrypted message from a file
def read_encrypted_message_from_file(filename):
    with open(filename, "rb") as file:
        encrypted_message = file.read()
    return encrypted_message

# Main program
if __name__ == "__main__":
    while True:
        print("\n1. Create a new user")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            create_user()
        elif choice == "2":
            username = login()
            if username:
                generate_key_pair(username)
                # Other functionalities like encryption and decryption can be added here

                while True:
                    print("\n1. Encrypt a message")
                    print("2. Decrypt a message")
                    print("3. Logout")
                    option = input("Enter your option: ")

                    if option == "1":
                        recipient = input("Enter recipient's username: ")
                        message = input("Enter message to encrypt: ")
                        user_data = load_user_data()
                        if recipient not in user_data:
                            print("Recipient not found!")
                            continue
                        recipient_public_key = user_data[recipient]["public_key"]
                        encrypted_message = encrypt_message(message, recipient_public_key)
                        filename = f"{username}_to_{recipient}.bin"
                        save_encrypted_message_to_file(filename, encrypted_message)
                        print("Encrypted message saved to file:", filename)
                        # print("Encrypted message:", encrypted_message.hex())

                    elif option == "2":
                        # encrypted_message = input("Enter encrypted message in hexadecimal format: ")
                        filename = input("Enter the filename containing the encrypted message: ")
                        user_data = load_user_data()
                        private_key = user_data[username]["private_key"]
                        encrypted_message = read_encrypted_message_from_file(filename)
                        print("Encrypted message:", encrypted_message)  # Debugging statement
                        decrypted_message = decrypt_message(encrypted_message, private_key)
                        print("Decrypted message:", decrypted_message)  # Debugging statement
                    
                    elif option == "3":
                        break
                    else:
                        print("Invalid option. Please try again.")
        
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
