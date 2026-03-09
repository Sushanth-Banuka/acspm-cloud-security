import hashlib
import db

def make_hashes(password):
    """
    Hashes a password with SHA-256.
    """
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """
    Checks if a password matches the hash.
    """
    if make_hashes(password) == hashed_text:
        return True
    return False

def init_users_db():
    """
    Initializes the database via db.py
    """
    db.init_db()

def login_user(username, password):
    """
    Verifies user credentials against the Database.
    """
    stored_hash = db.get_user_hash(username)
    if stored_hash:
        return check_hashes(password, stored_hash)
    return False

def create_user(username, password):
    """
    Adds a new user to the system.
    """
    hashed_pass = make_hashes(password)
    return db.create_user(username, hashed_pass)
