import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import getpass
import json
from PIL import Image
import steganography
from stegano import lsb

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
        json.dump(data, file, indent=4)

# Function to create a new user
def create_user():
    username = input("Enter a username: ")
    password = getpass.getpass("Enter a password: ")

    user_data = load_user_data()
    if username in user_data:
        print("User already exists!")
        return
    
    # Generate RSA key pair
    key = RSA.generate(1024)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # Store user data including keys
    user_data[username] = {"password": password, "private_key": private_key.decode(), "public_key": public_key.decode()}
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

# Function to encrypt a message
def encrypt_message(message, recipient_public_key):
    cipher = PKCS1_OAEP.new(RSA.import_key(recipient_public_key))
    encrypted_message = cipher.encrypt(message.encode())
    print("1.1.encrypt_message : ",encrypted_message)
    return encrypted_message

# Function to decrypt a message
def decrypt_message(encrypted_message, private_key, intended_recipient):
    try:  
        cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
        decrypted_message = cipher.decrypt(encrypted_message).decode()
        print("2.2.decrypt_message : ",encrypted_message)
        return decrypted_message
    except ValueError as e:
        print("Decryption error:", e)
        if private_key != load_user_data()[intended_recipient]["private_key"]:
            # raise ValueError("Invalid key!! Wrong User!!")
            print("Invalid key!! Wrong User!!")
        else:
            # raise ValueError("Incorrect decryption.")
            print("An error occurred during decryption!")

# Function to save encrypted message to a file
def save_encrypted_message_to_file(filename, encrypted_message):
    with open(filename, "wb") as file:
        file.write(encrypted_message)
    print("1.2.saved_encrypted_message : ",encrypted_message)

# Function to read encrypted message from a file
def read_encrypted_message_from_file(filename):
    with open(filename, "rb") as file:
        encrypted_message = file.read()
    print("read_encrypted_message : ",encrypted_message)
    return encrypted_message

# Function to hide encrypted message in an image using steganography
def hide_message_in_image(encrypted_message, cover_image_filename, stego_image_filename):
    # steganography.encode(encrypted_message, cover_image_filename, stego_image_filename)
    cover_image = cover_image_filename
    print("1.41.encrypt_message to hide : ",encrypted_message)

    encrypted_message_b64 = base64.b64encode(encrypted_message).decode()
    print("1.42.encrypt_message_b64 to hide : ",encrypted_message)

    stego_image = lsb.hide(cover_image, encrypted_message_b64)
    stego_image.save(stego_image_filename)
    print("1.5.Message encrypted and hidden in the image successfully!")
    print("1.6.stego_image_filename : ",stego_image_filename)

# Function to extract and decrypt message from stego image
def extract_and_decrypt_message(stego_image_filename, private_key, intended_recipient):
    # extracted_message = steganography.decode(stego_image_filename)
    encrypted_message_b64 = lsb.reveal(stego_image_filename)
    print("2.11.revealed encrypted_message_b64 : ",encrypted_message_b64)

    encrypted_message = base64.b64decode(encrypted_message_b64)
    print("2.12.revealed encrypted_message : ",encrypted_message)

    decrypted_message = decrypt_message(encrypted_message, private_key, intended_recipient)
    print("2.3.decrypted_message : ",decrypted_message)
    return decrypted_message


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

                        # Encrypt message using recipient's public key
                        encrypted_message = encrypt_message(message, recipient_public_key)
                        filename = f"{username}_to_{recipient}.bin"
                        save_encrypted_message_to_file(filename, encrypted_message)
                        print("1.3Encrypted message saved to file:", filename)
                        
                        # Embed encrypted message into the cover image
                        cover_image = input("Enter the cover image file name (with extension): ")
                        stego_image = f"{username}_to_{recipient}_stego.png"
                        # steganography.encode(encrypted_message, cover_image, f"{username}_to_{recipient}_steganographic.png")
                        hide_message_in_image(encrypted_message, cover_image, stego_image)
                        print("1.7.encoding to cover_image SUCCESS!")


                    elif option == "2":
                        user_data = load_user_data()
                        # filename = input("Enter the filename containing the encrypted message: ")
                        stego_image = input("Enter the received steganographic image file name (with extension): ")

                        intended_recipient = stego_image.split("_")[2]
                        private_key = user_data[username]["private_key"]
                        
                        # # Extract encrypted message from steganographic image
                        # steganography.decode(stego_image, f"{username}_to_{recipient}_extracted.bin")
                        
                        # encrypted_message = read_encrypted_message_from_file(f"{username}_to_{recipient}_extracted.bin")
                        # try:
                        #     decrypted_message = decrypt_message(encrypted_message, private_key, intended_recipient)
                        #     print("Decrypted message:", decrypted_message)
                        # except ValueError as e:
                        #     print("Error:", e)
                        
                        # Extract and decrypt message from steganographic image
                        decrypted_message = extract_and_decrypt_message(stego_image, private_key, intended_recipient)
                        print("Decrypted message:", decrypted_message)
                    
                    elif option == "3":
                        break
                    else:
                        print("Invalid option. Please try again.")
        
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
