import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import getpass
import json
# from PIL import Image
from stegano import lsb

def load_user_data():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open("users.json", "w") as file:
        json.dump(data, file, indent=4)

def create_user(user , pw):
    username = user
    password = pw

    user_data = load_user_data()
    if username in user_data:
        print("User already exists!")
        return
    
    key = RSA.generate(1024)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    user_data[username] = {"password": password, "private_key": private_key.decode(), "public_key": public_key.decode()}
    save_user_data(user_data)
    print("User created successfully!")

def loginUser(user, pw):
    username = user
    password = pw

    user_data = load_user_data()
    if username not in user_data or user_data[username]["password"] != password:
        # print("Invalid username or password!")
        return False

    # print("Login successful!")
    return True

def encrypt_message(message, recipient_public_key):
    cipher = PKCS1_OAEP.new(RSA.import_key(recipient_public_key))
    encrypted_message = cipher.encrypt(message.encode())
    # print("encrypted_message : ",encrypted_message)
    return encrypted_message

def save_encrypted_message_to_file(filename, encrypted_message):
    with open(filename, "wb") as file:
        file.write(encrypted_message)
    # print("1.2.saved_encrypted_message : ",encrypted_message)

def read_encrypted_message_from_file(filename):
    with open(filename, "rb") as file:
        encrypted_message = file.read()
    print("read_encrypted_message : ",encrypted_message)
    return encrypted_message

# Function to hide encrypted message in an image using steganography
# def hide_message_in_image(encrypted_message, cover_image_filename, stego_image_filename):
def hide_message_in_image(encrypted_message, cover_image_filename):
    cover_image = cover_image_filename
    # print("1.41.encrypted_message to hide : ",encrypted_message)

    encrypted_message_b64 = base64.b64encode(encrypted_message).decode()
    # print("1.5.encrypt_message_b64 to hide : ",encrypted_message)

    stego_image = lsb.hide(cover_image, encrypted_message_b64)
    # print("Message encrypted and hidden in the image successfully!")
    # print("1.6.stego_image_filename : ",stego_image_filename)
    return stego_image

def decrypt_message(encrypted_message, private_key, intended_recipient):
    try:  
        cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
        decrypted_message = cipher.decrypt(encrypted_message).decode()
        # print("2.2.decrypt_message : ",encrypted_message)
        return decrypted_message
    except ValueError as e:
        print("Decryption error:", e)
        if private_key != load_user_data()[intended_recipient]["private_key"]:
            print("Invalid key!! Wrong User!!")
        else:
            print("An error occurred during decryption!")

# Function to extract and decrypt message from stego image
def extract_and_decrypt_message(stego_image_path, private_key, intended_recipient):
    encrypted_message_b64 = lsb.reveal(stego_image_path)
    print("2.11.revealed encrypted_message_b64 : ", encrypted_message_b64)

    encrypted_message = base64.b64decode(encrypted_message_b64)
    print("2.12.revealed encrypted_message : ", encrypted_message)

    decrypted_message = decrypt_message(encrypted_message, private_key, intended_recipient)
    return decrypted_message


if __name__ == "__main__":
    while True:
        print("\n1. Create a new user")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            create_user()
        elif choice == "2":
            username = loginUser()
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
                        # print("1.3.Encrypted message saved to file:", filename)
                        
                        # Embed encrypted message into the cover image
                        cover_image = input("Enter the cover image file name (with extension): ")
                        stego_image = f"{username}_to_{recipient}_stego.png"
                        hide_message_in_image(encrypted_message, cover_image, stego_image)
                        # print("1.7.encoding to cover_image SUCCESS!")


                    elif option == "2":
                        user_data = load_user_data()
                        # filename = input("Enter the filename containing the encrypted message: ")
                        stego_image = input("Enter the received steganographic image file name (with extension): ")

                        intended_recipient = stego_image.split("_")[2]
                        private_key = user_data[username]["private_key"]
                        
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
