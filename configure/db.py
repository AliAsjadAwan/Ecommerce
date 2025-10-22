import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Global database connection
client = None
db = None

# Function to connect to MongoDB
def connect_db():
    global client, db
    try:
        # Retrieve the Mongo URI from environment variables
        uri = os.getenv('MONGO_URI')
        
        # Connect to MongoDB
        client = MongoClient(uri)
        db = client["Ecommerce"]  # Database name set to Ecommerce
        
        print('MongoDB connected to Ecommerce database')
        return db
    except Exception as err:
        print(f'MongoDB connection error: {err}')
        exit(1)  # Exit the script on error

# Function to get database instance
def get_db():
    global db
    if db is None:
        connect_db()
    return db

# Get collections
def get_collections():
    database = get_db()
    return {
        'products': database['products'],
        'users': database['users'],
        'orders': database['orders'],
        'reviews': database['reviews']
    }
