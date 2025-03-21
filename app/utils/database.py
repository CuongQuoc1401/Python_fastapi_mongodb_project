from pymongo import MongoClient
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv()

username_atlas = quote_plus("cuongquoc140102")
password_atlas = quote_plus("Cuongquoc@2002")
connection_string = f"mongodb+srv://{username_atlas}:{password_atlas}@cuongquoc.dvbmw.mongodb.net/python?retryWrites=true&w=majority"

client = MongoClient(connection_string)
db = client["python"]
users_collection = db["users"]
products_collection = db["products"]