import hashlib

def hash_password(password: str) -> str:
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed_password

def verify_password(provided_password: str, stored_password: str) -> bool:
    return provided_password == stored_password
# def verify_password(provided_password: str, stored_password: str) -> bool:
#     hashed_provided_password = hashlib.sha256(provided_password.encode('utf-8')).hexdigest()
#     return hashed_provided_password == stored_password

# import bcrypt

# def hash_password(password: str) -> str:
#     hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     return hashed_bytes.decode('utf-8')

# def verify_password(provided_password: str, stored_password: str) -> bool:
#     return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))