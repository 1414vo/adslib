from .config import *
import yaml

key = 'DataScience'

''' Encrypts a string with the Vigenere cypher
    :param key: The encryption key
    :param word: The string to be encrypted
    :return: The encrypted word
'''
def encrypt(key, word):
    encrypted = ""
    for ind, char in enumerate(word):
        encrypted += chr(ord(char) + ord(key[ind % len(key)]))
    return encrypted

''' Decrypts a string with the Vigenere cypher
    :param key: The encryption key
    :param word: The string to be decrypted
    :return: The decrypted word
'''
def decrypt(key, word):
    decrypted = ""
    for ind, char in enumerate(word):
        decrypted += chr(ord(char) - ord(key[ind % len(key)]))
    return decrypted

''' Encrypts and stores the credentials within a given file
    :param username: The username to be stored
    :param password: The password to be stored
'''
def store_creds(username, password, filename):
    with open(filename, "w") as file:
        credentials_dict = {'username': encrypt(key, username),
                            'password': encrypt(key, password)}
        yaml.dump(credentials_dict, file)

''' Loads and decrypts the credentials from a file
    :param filename: The location of the credentials file
    :return: A tuple of the credentials
'''
def load_creds(filename):

    with open(filename) as file:
        credentials = yaml.safe_load(file)
    username = decrypt(key, credentials["username"])
    password = decrypt(key, credentials["password"])

    return username, password