from app.models.user_model import users_collection
from app.utils.security import verify_password

def authenticate_user(username, password):
    print(f"Authenticating user: {username}")
    user = users_collection.find_one({"username": username})
    print(f"User found: {user}")
    if user and verify_password(user["password"], password):
        print("Authentication successful")
        return user
    print("Authentication failed")
    return None

def authenticate_username(username):
    user = users_collection.find_one({"username": username})
    if user:
        return user
    return None