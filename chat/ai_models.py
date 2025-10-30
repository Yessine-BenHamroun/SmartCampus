"""
Modèles MongoDB pour l'analyse AI des messages
"""
from datetime import datetime
from bson import ObjectId


class MessageSentiment:
    """Modèle pour stocker l'analyse de sentiment des messages"""
    
    COLLECTION_NAME = 'message_sentiments'
    
    @staticmethod
    def create(message_id, sentiment, score, emoji, analyzed_at=None):
        """
        Créer une nouvelle analyse de sentiment
        
        Args:
            message_id: ID du message MongoDB
            sentiment: POSITIVE, NEGATIVE, NEUTRAL
            score: Score de confiance (0-1)
            emoji: Emoji associé
            analyzed_at: Date d'analyse
            
        Returns:
            dict: Document créé
        """
        from chat.mongodb_manager import MongoDBChatManager
        
        manager = MongoDBChatManager()
        collection = manager.db[MessageSentiment.COLLECTION_NAME]
        
        document = {
            'message_id': ObjectId(message_id) if isinstance(message_id, str) else message_id,
            'sentiment': sentiment,
            'score': score,
            'emoji': emoji,
            'analyzed_at': analyzed_at or datetime.utcnow()
        }
        
        result = collection.insert_one(document)
        document['_id'] = result.inserted_id
        
        return document
    
    @staticmethod
    def find_by_message(message_id):
        """Trouver l'analyse de sentiment d'un message"""
        from chat.mongodb_manager import MongoDBChatManager
        
        manager = MongoDBChatManager()
        collection = manager.db[MessageSentiment.COLLECTION_NAME]
        
        return collection.find_one({
            'message_id': ObjectId(message_id) if isinstance(message_id, str) else message_id
        })
    
    @staticmethod
    def get_room_sentiment_stats(room_id, limit=100):
        """
        Obtenir les statistiques de sentiment d'un salon
        
        Args:
            room_id: ID du salon
            limit: Nombre de messages à analyser
            
        Returns:
            dict: Statistiques de sentiment
        """
        from chat.mongodb_manager import MongoDBChatManager
        from chat.mongo_models import ChatMessageMongo
        
        manager = MongoDBChatManager()
        sentiments_col = manager.db[MessageSentiment.COLLECTION_NAME]
        
        # Récupérer les derniers messages du salon
        messages = ChatMessageMongo.get_room_messages(room_id, limit=limit)
        message_ids = [msg['_id'] for msg in messages]
        
        # Récupérer les sentiments
        sentiments = list(sentiments_col.find({
            'message_id': {'$in': message_ids}
        }))
        
        if not sentiments:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0
            }
        
        total = len(sentiments)
        positive = sum(1 for s in sentiments if s['sentiment'] == 'POSITIVE')
        negative = sum(1 for s in sentiments if s['sentiment'] == 'NEGATIVE')
        neutral = sum(1 for s in sentiments if s['sentiment'] == 'NEUTRAL')
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_percentage': round((positive / total) * 100, 2),
            'negative_percentage': round((negative / total) * 100, 2),
            'neutral_percentage': round((neutral / total) * 100, 2)
        }


class ConversationInsights:
    """Modèle pour stocker les insights de conversation"""
    
    COLLECTION_NAME = 'conversation_insights'
    
    @staticmethod
    def create(room_id, insights_data):
        """
        Créer un rapport d'insights pour une conversation
        
        Args:
            room_id: ID du salon
            insights_data: Données d'analyse
            
        Returns:
            dict: Document créé
        """
        from chat.mongodb_manager import MongoDBChatManager
        
        manager = MongoDBChatManager()
        collection = manager.db[ConversationInsights.COLLECTION_NAME]
        
        document = {
            'room_id': ObjectId(room_id) if isinstance(room_id, str) else room_id,
            'created_at': datetime.utcnow(),
            **insights_data
        }
        
        result = collection.insert_one(document)
        document['_id'] = result.inserted_id
        
        return document
    
    @staticmethod
    def get_latest_insights(room_id):
        """Obtenir les derniers insights d'un salon"""
        from chat.mongodb_manager import MongoDBChatManager
        
        manager = MongoDBChatManager()
        collection = manager.db[ConversationInsights.COLLECTION_NAME]
        
        return collection.find_one(
            {'room_id': ObjectId(room_id) if isinstance(room_id, str) else room_id},
            sort=[('created_at', -1)]
        )
