"""
Gestionnaire MongoDB pour le chat
Utilise pymongo directement pour une meilleure performance
"""
import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId


class MongoDBChatManager:
    """Gestionnaire de connexion MongoDB pour le chat"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBChatManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            # Connexion MongoDB
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGO_DB_NAME', 'smartcampus_db')  # ✅ Correspond à settings.py
            
            self._client = MongoClient(mongo_uri)
            self._db = self._client[db_name]
            
            print(f"✅ Connecté à MongoDB: {db_name}")
            
            # Créer les index
            self._create_indexes()
    
    def _create_indexes(self):
        """Créer les index pour améliorer les performances"""
        try:
            # Index pour les salons
            self._db.chat_rooms.create_index('slug', unique=True)
            self._db.chat_rooms.create_index('room_type')
            self._db.chat_rooms.create_index('is_active')
            
            # Index pour les messages
            self._db.chat_messages.create_index('room_id')
            self._db.chat_messages.create_index('timestamp')
            self._db.chat_messages.create_index([('room_id', 1), ('timestamp', -1)])
            
            # Index pour les participants
            self._db.chat_participants.create_index([('room_id', 1), ('user_id', 1)], unique=True)
            self._db.chat_participants.create_index('is_online')
            
            print("✅ Index MongoDB créés")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création des index: {e}")
    
    @property
    def db(self):
        """Retourne la base de données"""
        return self._db
    
    @property
    def rooms(self):
        """Collection des salons"""
        return self._db.chat_rooms
    
    @property
    def messages(self):
        """Collection des messages"""
        return self._db.chat_messages
    
    @property
    def participants(self):
        """Collection des participants"""
        return self._db.chat_participants


# Instance globale
mongodb = MongoDBChatManager()
