"""
API Views pour l'intégration AI dans le chat
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from .ai_sentiment import get_sentiment_analyzer
from .ai_models import MessageSentiment, ConversationInsights
from .mongo_models import ChatMessageMongo, ChatRoomMongo


@login_required
@require_http_methods(["POST"])
def analyze_message_sentiment(request):
    """
    API pour analyser le sentiment d'un message
    
    POST /chat/api/ai/analyze-sentiment/
    Body: {
        "message_id": "...",
        "text": "..."
    }
    """
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        text = data.get('text')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text is required'
            }, status=400)
        
        # Analyser le sentiment
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_message(text)
        
        # Sauvegarder dans MongoDB si message_id fourni
        if message_id:
            MessageSentiment.create(
                message_id=message_id,
                sentiment=result['sentiment'],
                score=result['score'],
                emoji=result['emoji']
            )
        
        return JsonResponse({
            'success': True,
            'analysis': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_room_sentiment_stats(request, room_slug):
    """
    Obtenir les statistiques de sentiment d'un salon
    
    GET /chat/api/ai/room/<room_slug>/sentiment-stats/
    """
    try:
        # Récupérer le salon
        room = ChatRoomMongo.get_by_slug(room_slug)
        
        if not room:
            return JsonResponse({
                'success': False,
                'error': 'Room not found'
            }, status=404)
        
        # Vérifier que l'utilisateur a accès
        room_id = str(room['_id'])
        
        # Obtenir les statistiques
        stats = MessageSentiment.get_room_sentiment_stats(room_id)
        
        return JsonResponse({
            'success': True,
            'room_slug': room_slug,
            'sentiment_stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def analyze_conversation(request, room_slug):
    """
    Analyser toute une conversation et générer des insights
    
    POST /chat/api/ai/room/<room_slug>/analyze/
    """
    try:
        # Récupérer le salon
        room = ChatRoomMongo.get_by_slug(room_slug)
        
        if not room:
            return JsonResponse({
                'success': False,
                'error': 'Room not found'
            }, status=404)
        
        room_id = str(room['_id'])
        
        # Récupérer les messages récents
        messages = ChatMessageMongo.get_room_messages(room_id, limit=100, include_deleted=False)
        
        if not messages:
            return JsonResponse({
                'success': True,
                'message': 'No messages to analyze',
                'insights': None
            })
        
        # Extraire les textes
        texts = [msg['content'] for msg in messages if msg.get('content')]
        
        # Analyser l'ambiance de la conversation
        analyzer = get_sentiment_analyzer()
        mood = analyzer.get_conversation_mood(texts)
        
        # Analyser chaque message et sauvegarder
        analyses = analyzer.analyze_batch(texts)
        
        for i, analysis in enumerate(analyses):
            if i < len(messages):
                message_id = messages[i]['_id']
                
                # Vérifier si l'analyse existe déjà
                existing = MessageSentiment.find_by_message(message_id)
                
                if not existing:
                    MessageSentiment.create(
                        message_id=message_id,
                        sentiment=analysis['sentiment'],
                        score=analysis['score'],
                        emoji=analysis['emoji']
                    )
        
        # Créer un rapport d'insights
        insights_data = {
            'total_messages_analyzed': len(messages),
            'overall_mood': mood['overall_mood'],
            'sentiment_distribution': {
                'positive': mood['positive_percentage'],
                'negative': mood['negative_percentage'],
                'neutral': mood['neutral_percentage']
            },
            'recommendations': generate_recommendations(mood)
        }
        
        # Sauvegarder les insights
        ConversationInsights.create(room_id, insights_data)
        
        return JsonResponse({
            'success': True,
            'insights': insights_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_message_sentiment(request, message_id):
    """
    Obtenir le sentiment d'un message spécifique
    
    GET /chat/api/ai/message/<message_id>/sentiment/
    """
    try:
        sentiment = MessageSentiment.find_by_message(message_id)
        
        if not sentiment:
            return JsonResponse({
                'success': False,
                'error': 'Sentiment analysis not found'
            }, status=404)
        
        # Convertir ObjectId en string
        sentiment['_id'] = str(sentiment['_id'])
        sentiment['message_id'] = str(sentiment['message_id'])
        
        return JsonResponse({
            'success': True,
            'sentiment': sentiment
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def generate_recommendations(mood):
    """
    Générer des recommandations basées sur l'ambiance de la conversation
    
    Args:
        mood (dict): Statistiques d'ambiance
        
    Returns:
        list: Liste de recommandations
    """
    recommendations = []
    
    negative_pct = mood.get('negative_percentage', 0)
    positive_pct = mood.get('positive_percentage', 0)
    
    if negative_pct > 30:
        recommendations.append({
            'type': 'warning',
            'message': "L'ambiance semble négative. Envisagez d'intervenir pour améliorer le climat de discussion."
        })
    
    if negative_pct > 50:
        recommendations.append({
            'type': 'alert',
            'message': "Attention : Forte proportion de messages négatifs détectée. Une modération peut être nécessaire."
        })
    
    if positive_pct > 70:
        recommendations.append({
            'type': 'success',
            'message': "Excellente ambiance de discussion ! Les échanges sont constructifs."
        })
    
    if 40 <= positive_pct <= 60 and 40 <= mood.get('neutral_percentage', 0) <= 60:
        recommendations.append({
            'type': 'info',
            'message': "Discussion équilibrée. L'ambiance est neutre et professionnelle."
        })
    
    return recommendations
