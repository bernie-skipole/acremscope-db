
import os, psycopg2, hashlib


# This is the project name
_PROJECT = "acremscope"


def hash_password(project, user_id, password):
    "Return hashed password, as a string, on failure return None"
    seed_password = project + str(user_id) +  password
    hashed_password = hashlib.sha512(   seed_password.encode('utf-8')  ).digest().hex()
    return hashed_password


def hash_pin(pinpair, project, user_id, pos):
    "Return hashed pin pair, as a string, on failure return None"
    seed_pin = project + str(user_id) + str(pos) +  pinpair
    hashed_pin = hashlib.sha512(   seed_pin.encode('utf-8')  ).digest().hex()
    return hashed_pin


if __name__ == "__main__":

    password = input(f"Input a new password for user id 1:")

    new_pin = input("Input a new pin:")

    con = psycopg2.connect(dbname='astrodb', user='astro', password='xxSgham', host='localhost')

    pwd = hash_password(_PROJECT, 1, password)

    cur = con.cursor()

    cur.execute("update users set password = %s where user_id = %s", (pwd, 1))

    pin1_2 = hash_pin(new_pin[0] + new_pin[1], _PROJECT, 1, 1)
    pin1_3 = hash_pin(new_pin[0] + new_pin[2], _PROJECT, 1, 2)
    pin1_4 = hash_pin(new_pin[0] + new_pin[3], _PROJECT, 1, 3)
    pin2_3 = hash_pin(new_pin[1] + new_pin[2], _PROJECT, 1, 4)
    pin2_4 = hash_pin(new_pin[1] + new_pin[3], _PROJECT, 1, 5)
    pin3_4 = hash_pin(new_pin[2] + new_pin[3], _PROJECT, 1, 6)

    cur.execute("""insert into admins (user_id, pin1_2, pin1_3, pin1_4, pin2_3, pin2_4, pin3_4) values (%s, %s, %s, %s, %s, %s, %s)
                   on conflict (user_id) do update set pin1_2 = %s, pin1_3 = %s, pin1_4 = %s, pin2_3 = %s, pin2_4 = %s, pin3_4 = %s""",
                (1, pin1_2, pin1_3, pin1_4, pin2_3, pin2_4, pin3_4, pin1_2, pin1_3, pin1_4, pin2_3, pin2_4, pin3_4))

    con.commit()
    con.close()

    print(f"Password Hash: {pwd}")
    print("Pin pair Hashes:")
    print(pin1_2)
    print(pin1_3)
    print(pin1_4)
    print(pin2_3)
    print(pin2_4)
    print(pin3_4)

