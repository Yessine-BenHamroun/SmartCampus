"""
MongoDB database connection utilities
"""
from pymongo import MongoClient
from django.conf import settings

_client = None
_db = None


def get_mongo_client():
    """Get MongoDB client singleton"""
    global _client
    if _client is None:
        print(f"🔌 Connecting to MongoDB: {settings.MONGODB_SETTINGS['host']}")
        _client = MongoClient(settings.MONGODB_SETTINGS['host'])
        print(f"✅ MongoDB client connected")
    return _client


def get_database():
    """Get MongoDB database singleton"""
    global _db
    if _db is None:
        client = get_mongo_client()
        db_name = settings.MONGODB_SETTINGS['db_name']
        print(f"📂 Using database: {db_name}")
        _db = client[db_name]
    return _db


def get_collection(collection_name):
    """Get MongoDB collection"""
    db = get_database()
    print(f"📊 Accessing collection: {collection_name}")
    return db[collection_name]


def close_mongo_connection():
    """Close MongoDB connection"""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
