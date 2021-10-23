from Crypto.Cipher import AES
import os
import base64

block_size = 16
secret = os.environ["ENCRYPTION_SECRET"]


def un_pad(word):
    """
        Removes additional padding from string
    :param word: <string>
    :return: string after removing padding from it <string>
    """
    padding_length = ord(word[len(word) - 1:])
    un_padded_word = word[:-padding_length]
    return un_padded_word


def pad(word):
    length = block_size - (len(word) % block_size)
    word += bytes([length]) * length
    return word


def encrypt(my_string):
    private_key = secret[0:32].encode()
    initialisation_vector = secret[0:16].encode()
    cipher = AES.new(private_key, AES.MODE_CBC, initialisation_vector)
    my_string = my_string.encode()
    my_string = pad(my_string)
    encrypted_string = cipher.encrypt(my_string)
    encrypted_string = base64.b64encode(encrypted_string)
    return encrypted_string.decode()


def decrypt(encrypted_string):
    private_key = secret[0:32].encode()
    initialisation_vector = secret[0:16].encode()
    cipher = AES.new(private_key, AES.MODE_CBC, initialisation_vector)
    decrypted_string = base64.b64decode(encrypted_string)
    decrypted_string = cipher.decrypt(decrypted_string)
    decrypted_string = un_pad(decrypted_string)
    return decrypted_string.decode()


if __name__ == "__main__":
    this_string = "Hello, I am Gaurav. Nice to meet you!"
    print(this_string)
    r_encrypted_string = encrypt(this_string)
    print(r_encrypted_string)
    r_decrypted_string = decrypt(r_encrypted_string)
    print(r_decrypted_string)
