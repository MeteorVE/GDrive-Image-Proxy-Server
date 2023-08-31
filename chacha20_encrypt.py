# !pip install pycryptodome
import json
from base64 import b64encode
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

def encrypt_with_chacha20(plaintext, key, nonce):
    cipher = ChaCha20.new(key=key, nonce=nonce)
    ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
    encoded_ciphertext = b64encode(ciphertext).decode('utf-8')
    return encoded_ciphertext

def decrypt_with_chacha20(ciphertext, key, nonce):
    cipher2 = ChaCha20.new(key=key, nonce=nonce)
    decrypted_data = cipher2.decrypt(ciphertext)
    decrypted_text = decrypted_data.decode('utf-8')
    return decrypted_text