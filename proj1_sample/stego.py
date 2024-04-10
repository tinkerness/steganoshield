from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from PIL import Image
import base64

# Generate RSA key pair
key = RSA.generate(2048)

# Get the public and private keys
public_key = key.publickey()
private_key = key

# Encrypt the message
def encrypt_message(message, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

# Decrypt the message
def decrypt_message(encrypted_message, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode()

# LSB Steganography functions
def set_bit(value, bit):
    return value | bit

def clear_bit(value, bit):
    return value & ~bit

def hide_message(image_path, message):
    img = Image.open(image_path)
    pixels = img.load()
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_message += '1111111111111110'  # End of message marker

    index = 0
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = pixels[i, j]

            r = clear_bit(r, 1)
            r = set_bit(r, int(binary_message[index]))
            index += 1

            if index == len(binary_message):
                pixels[i, j] = (r, g, b)
                img.save('stego_image.png')
                return

# Example usage
message = "Hello, this is a secret message!"
encrypted_message = encrypt_message(message, public_key)
encrypted_message_base64 = base64.b64encode(encrypted_message)  # Convert bytes to Base64 string
hide_message('cover_image.png', encrypted_message_base64.decode())  # Decode Base64 to string before hiding
# hide_message('cover_image.png', encrypted_message)

# To decrypt the message from the steganographic image and display it
def extract_message(image_path):
    img = Image.open(image_path)
    pixels = img.load()

    binary_message = ''
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, _, _ = pixels[i, j]
            binary_message += str(r & 1)

            if binary_message[-16:] == '1111111111111110':  # Check for end of message marker
                binary_message = binary_message[:-16]  # Remove end of message marker
                return binary_message.rstrip('0')  # Remove any trailing zeros (padding)

def display_message(encrypted_message, private_key):
    try:
        decrypted_message = decrypt_message(encrypted_message, private_key)
        print("Decrypted Message:", decrypted_message)
    except ValueError as e:
        print("Error decrypting the message:", e)
    except Exception as e:
        print("An unexpected error occurred during decryption:", e)

# Example usage
stego_image_path = 'stego_image.png'
extracted_message = extract_message(stego_image_path)

# Decode Base64 string back to bytes
extracted_message_bytes = base64.b64decode(extracted_message)
display_message(extracted_message_bytes, private_key)
