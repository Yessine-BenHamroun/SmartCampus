"""
Script de migration SQLite vers MongoDB pour le chat
Exécuter ce script pour migrer les données existantes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')
django.setup()

from chat.models import ChatRoom, ChatMessage, ChatParticipant
from chat.mongo_models import ChatRoomMongo, ChatMessageMongo, ChatParticipantMongo

print("=" * 70)
print("🔄 MIGRATION DU CHAT: SQLite → MongoDB")
print("=" * 70)

# Migrer les salons
print("\n📦 Migration des salons de chat...")
rooms = ChatRoom.objects.all()
print(f"   Trouvé {rooms.count()} salons dans SQLite")

for room in rooms:
    try:
        existing = ChatRoomMongo.get_by_slug(room.slug)
        if existing:
            print(f"   ⚠️  Salon '{room.name}' existe déjà dans MongoDB")
            continue
        
        mongo_room = ChatRoomMongo.create(
            name=room.name,
            slug=room.slug,
            room_type=room.room_type,
            description=room.description,
            created_by_id=room.created_by.id,
            created_by_email=room.created_by.email,
            created_by_name=f"{room.created_by.first_name} {room.created_by.last_name}".strip() or room.created_by.username,
            participant_ids=list(room.participants.values_list('id', flat=True))
        )
        print(f"   ✅ Salon '{room.name}' migré (ID MongoDB: {mongo_room['_id']})")
    except Exception as e:
        import traceback
        print(f"   ❌ Erreur pour '{room.name}': {e}")
        traceback.print_exc()

# Migrer les participants
print("\n👥 Migration des participants...")
participants = ChatParticipant.objects.all()
print(f"   Trouvé {participants.count()} participants dans SQLite")

for participant in participants:
    try:
        mongo_room = ChatRoomMongo.get_by_slug(participant.room.slug)
        if not mongo_room:
            print(f"   ⚠️  Salon '{participant.room.slug}' introuvable dans MongoDB")
            continue
        
        ChatParticipantMongo.get_or_create(
            room_id=str(mongo_room['_id']),
            user_id=participant.user.id,
            user_email=participant.user.email,
            user_name=f"{participant.user.first_name} {participant.user.last_name}".strip() or participant.user.username
        )
        print(f"   ✅ Participant {participant.user.username} → {participant.room.name}")
    except Exception as e:
        import traceback
        print(f"   ❌ Erreur: {e}")
        traceback.print_exc()

# Migrer les messages
print("\n💬 Migration des messages...")
messages = ChatMessage.objects.filter(is_deleted=False)
print(f"   Trouvé {messages.count()} messages dans SQLite")

for message in messages:
    try:
        mongo_room = ChatRoomMongo.get_by_slug(message.room.slug)
        if not mongo_room:
            print(f"   ⚠️  Salon '{message.room.slug}' introuvable")
            continue
        
        ChatMessageMongo.create(
            room_id=str(mongo_room['_id']),
            sender_id=message.sender.id,
            sender_email=message.sender.email,
            sender_name=f"{message.sender.first_name} {message.sender.last_name}".strip() or message.sender.username,
            content=message.content
        )
        print(f"   ✅ Message de {message.sender.username} migré")
    except Exception as e:
        import traceback
        print(f"   ❌ Erreur: {e}")
        traceback.print_exc()

print("\n" + "=" * 70)
print("✅ MIGRATION TERMINÉE")
print("=" * 70)

# Statistiques finales
from chat.mongodb_manager import mongodb

print("\n📊 Statistiques MongoDB:")
print(f"   - Salons: {mongodb.rooms.count_documents({})}")
print(f"   - Messages: {mongodb.messages.count_documents({})}")
print(f"   - Participants: {mongodb.participants.count_documents({})}")

print("\n🎉 Le chat utilise maintenant MongoDB !")
print("   Base de données: smartcampus_db")
print("   Collections: chat_rooms, chat_messages, chat_participants")
