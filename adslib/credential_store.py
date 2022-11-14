import yaml

key = 'DataScience'

def encrypt(key, word):
    encrypted = ""
    for ind, char in enumerate(word):
        encrypted += chr(ord(char) + ord(key[ind % len(key)]))
    return encrypted

def decrypt(key, word):
    decrypted = ""
    for ind, char in enumerate(word):
        decrypted += chr(ord(char) - ord(key[ind % len(key)]))
    return decrypted

def store_creds(username, password, filename):
    with open(filename, "w") as file:
        credentials_dict = {'username': encrypt(key, username),
                            'password': encrypt(key, password)}
        yaml.dump(credentials_dict, file)

def load_creds(filename):

    with open(filename) as file:
        credentials = yaml.safe_load(file)
    username = decrypt(key, credentials["username"])
    password = decrypt(key, credentials["password"])

    return username, password