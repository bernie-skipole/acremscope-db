
import hashlib


def hash_password(password):
    "Return hashed password, as a string, on failure return None"
    seed_password = "1234554321" +  password
    hashed_password = hashlib.sha512(   seed_password.encode('utf-8')  ).hexdigest()
    return hashed_password


if __name__ == "__main__":

    password = input("Password:")
    print(hash_password(password))
