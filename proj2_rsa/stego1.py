from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Key generation
def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Encryption
def encrypt_message(message, public_key):
    cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

# Decryption
def decrypt_message(encrypted_message, private_key):
    cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
    decrypted_message = cipher.decrypt(encrypted_message).decode()
    return decrypted_message

# Example usage
if __name__ == "__main__":
    # Generate keys for Alice and Bob
    alice_private_key, alice_public_key = generate_key_pair()
    bob_private_key, bob_public_key = generate_key_pair()

    # Alice encrypts a message for Bob
    message = "Hello Bob, this is Alice!"
    encrypted_message = encrypt_message(message, bob_public_key)

    # Bob decrypts the message
    decrypted_message = decrypt_message(encrypted_message, bob_private_key)
    print("Decrypted message:", decrypted_message)
