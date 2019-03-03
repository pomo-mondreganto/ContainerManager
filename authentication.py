import hashlib
import secrets

import helpers


def get_password_hash(password):
    salt = secrets.token_hex(16)
    result = hashlib.sha1((password + salt).encode()).hexdigest()
    return result, salt


def check_password(password, password_hash, salt):
    result = hashlib.sha1((password + salt).encode()).hexdigest()
    return result == password_hash


def authenticate_user(login, password):
    conn, cur = helpers.get_connection_cursor(return_named=True)

    query = "SELECT * from User WHERE login=?"
    cur.execute(query, (login,))
    user = dict(cur.fetchone() or {})

    if check_password(password=password, password_hash=user.get('password_hash', ''), salt=user.get('salt', '')):
        return user
    return None
