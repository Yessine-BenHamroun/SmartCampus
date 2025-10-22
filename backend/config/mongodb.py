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
        _client = MongoClient(settings.MONGODB_SETTINGS['host'])
    return _client


def get_database():
    """Get MongoDB database singleton"""
    global _db
    if _db is None:
        client = get_mongo_client()
        _db = client[settings.MONGODB_SETTINGS['db_name']]
    return _db


def get_collection(collection_name):
    """Get MongoDB collection"""
    db = get_database()
    return db[collection_name]


def close_mongo_connection():
    """Close MongoDB connection"""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
