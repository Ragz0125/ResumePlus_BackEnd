from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()
from loggers import db_logger

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION")

client = MongoClient(MONGO_CONNECTION_STRING)
client.admin.command("ping")

try:
    client.admin.command("ping")
    print("Connected to MongoDb")
except Exception as e:
    print(f"Connection failed to MongoDb: {e}")

def get_mongo_db():
    mongo_db = client["resume_plus"] 
    return mongo_db

