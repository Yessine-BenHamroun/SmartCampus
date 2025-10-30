"""
Script pour vérifier le contenu de MongoDB pour le chat
"""
import os
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017/')
os.environ.setdefault('MONGO_DB_NAME', 'smartcampus')  # Correspond à settings.py

from chat.mongodb_manager import mongodb

print("=" * 70)
print("🔍 VÉRIFICATION DU CONTENU MONGODB - CHAT")
print("=" * 70)

# Vérifier les salons
print("\n📦 SALONS DE CHAT:")
rooms = list(mongodb.rooms.find())
print(f"Nombre de salons: {len(rooms)}")
for room in rooms:
    print(f"\n  Salon: {room.get('name')}")
    print(f"  - ID: {room.get('_id')}")
    print(f"  - Slug: {room.get('slug')}")
    print(f"  - Type: {room.get('room_type')}")
    print(f"  - Participants: {room.get('participant_ids', [])}")

# Vérifier les messages
print("\n💬 MESSAGES:")
messages = list(mongodb.messages.find())
print(f"Nombre de messages: {len(messages)}")
if messages:
    for i, msg in enumerate(messages[:5], 1):  # Afficher les 5 premiers
        print(f"\n  Message {i}:")
        print(f"  - ID: {msg.get('_id')}")
        print(f"  - Room ID: {msg.get('room_id')}")
        print(f"  - Sender: {msg.get('sender_name')}")
        print(f"  - Content: {msg.get('content')[:50]}...")
        print(f"  - Timestamp: {msg.get('timestamp')}")

# Vérifier les participants
print("\n👥 PARTICIPANTS:")
participants = list(mongodb.participants.find())
print(f"Nombre de participants: {len(participants)}")
for part in participants:
    print(f"\n  Participant:")
    print(f"  - User: {part.get('user_name')}")
    print(f"  - Room ID: {part.get('room_id')}")
    print(f"  - Online: {part.get('is_online')}")

print("\n" + "=" * 70)
print("✅ Vérification terminée")
