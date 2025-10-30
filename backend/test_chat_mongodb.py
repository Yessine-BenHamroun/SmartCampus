"""
Script de test pour vérifier la connexion MongoDB et créer des données de chat
"""
import os
import sys
import django
from datetime import datetime

# Configuration de Django
sys.path.append(r'C:\Users\taher\OneDrive\Desktop\Django\SmartCampus\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chat.models import ChatRoom, ChatMessage, ChatParticipant

print("=" * 60)
print("🧪 TEST DE CONNEXION MONGODB POUR LE CHAT")
print("=" * 60)

# Test 1: Créer un salon de chat
print("\n📝 Test 1: Création d'un salon de chat...")
try:
    room = ChatRoom.objects.create(
        name="Salon Test MongoDB",
        slug="test-mongodb",
        room_type="public",
        description="Salon de test pour MongoDB",
        created_by_id=1,
        created_by_email="test@example.com",
        created_by_name="Test User",
        participant_ids=[1]
    )
    print(f"✅ Salon créé avec succès: {room.name} (ID: {room._id})")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Lister les salons
print("\n📋 Test 2: Liste des salons...")
try:
    rooms = ChatRoom.objects.all()
    print(f"✅ Nombre de salons: {rooms.count()}")
    for room in rooms:
        print(f"   - {room.name} ({room.room_type}) - Créé par: {room.created_by_name}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Créer un message
print("\n💬 Test 3: Création d'un message...")
try:
    if ChatRoom.objects.exists():
        room = ChatRoom.objects.first()
        message = ChatMessage.objects.create(
            room_id=str(room._id),
            sender_id=1,
            sender_email="test@example.com",
            sender_name="Test User",
            content="Ceci est un message de test dans MongoDB !"
        )
        print(f"✅ Message créé: {message.content[:50]}...")
    else:
        print("⚠️ Aucun salon disponible pour tester les messages")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 4: Lister les messages
print("\n📨 Test 4: Liste des messages...")
try:
    messages = ChatMessage.objects.all()
    print(f"✅ Nombre de messages: {messages.count()}")
    for msg in messages:
        print(f"   - {msg.sender_name}: {msg.content[:50]}...")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 5: Créer un participant
print("\n👤 Test 5: Ajout d'un participant...")
try:
    if ChatRoom.objects.exists():
        room = ChatRoom.objects.first()
        participant = ChatParticipant.objects.create(
            room_id=str(room._id),
            user_id=1,
            user_email="test@example.com",
            user_name="Test User",
            is_online=True
        )
        print(f"✅ Participant ajouté: {participant.user_name}")
    else:
        print("⚠️ Aucun salon disponible")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS")
print("=" * 60)
print("\n📊 Résumé:")
print(f"   - Salons: {ChatRoom.objects.count()}")
print(f"   - Messages: {ChatMessage.objects.count()}")
print(f"   - Participants: {ChatParticipant.objects.count()}")
print("\n🎉 Le chat est maintenant stocké dans MongoDB !")
print("   Base de données: smartcampus_db")
print("   Collections: chat_rooms, chat_messages, chat_participants")
