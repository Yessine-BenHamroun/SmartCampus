"""
Script de test pour déboguer l'API AI
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')
django.setup()

from chat.ai_sentiment import get_sentiment_analyzer
from chat.mongo_models import ChatMessageMongo, ChatRoomMongo

print("🔍 Test de débogage de l'API AI\n")
print("=" * 60)

# 1. Tester le chargement de l'analyzer
print("\n1. Test du chargement de l'analyzer...")
try:
    analyzer = get_sentiment_analyzer()
    print("   ✅ Analyzer chargé avec succès")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

# 2. Tester une analyse simple
print("\n2. Test d'analyse simple...")
try:
    result = analyzer.analyze_message("This is amazing!")
    print(f"   ✅ Analyse réussie: {result['sentiment']} {result['emoji']}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 3. Récupérer un salon de test
print("\n3. Récupération d'un salon...")
try:
    rooms = ChatRoomMongo.get_all()
    if rooms:
        room = rooms[0]
        room_id = str(room['_id'])
        room_slug = room['slug']
        print(f"   ✅ Salon trouvé: {room['name']} (slug: {room_slug})")
        
        # 4. Récupérer les messages
        print("\n4. Récupération des messages...")
        messages = ChatMessageMongo.get_room_messages(room_id, limit=10)
        print(f"   ✅ {len(messages)} messages trouvés")
        
        if messages:
            # 5. Extraire les textes
            print("\n5. Extraction des textes...")
            texts = [msg['content'] for msg in messages if msg.get('content')]
            print(f"   ✅ {len(texts)} textes extraits")
            
            for i, text in enumerate(texts[:3], 1):
                print(f"      {i}. \"{text[:50]}...\"" if len(text) > 50 else f"      {i}. \"{text}\"")
            
            # 6. Analyser l'ambiance
            print("\n6. Analyse de l'ambiance...")
            try:
                mood = analyzer.get_conversation_mood(texts)
                print(f"   ✅ Mood: {mood['overall_mood']}")
                print(f"      - Positif: {mood['positive_percentage']}%")
                print(f"      - Négatif: {mood['negative_percentage']}%")
                print(f"      - Neutre: {mood['neutral_percentage']}%")
            except Exception as e:
                print(f"   ❌ Erreur lors de l'analyse: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ⚠️  Aucun message à analyser")
    else:
        print("   ⚠️  Aucun salon trouvé")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Test terminé")
