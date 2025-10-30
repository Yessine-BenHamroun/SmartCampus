"""
Script de debug pour vérifier les sender_id dans MongoDB
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')
import django
django.setup()

from chat.mongodb_manager import mongodb
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("🔍 DEBUG: Vérification des sender_id")
print("=" * 70)

# Récupérer un utilisateur
user = User.objects.first()
print(f"\n👤 User: {user.username}")
print(f"   - user.id: {user.id} (type: {type(user.id).__name__})")
print(f"   - user.pk: {user.pk} (type: {type(user.pk).__name__})")

# Récupérer quelques messages
messages = list(mongodb.messages.find().limit(5))
print(f"\n💬 Messages dans MongoDB:")
for i, msg in enumerate(messages, 1):
    print(f"\n   Message {i}:")
    print(f"   - sender_id: {msg.get('sender_id')} (type: {type(msg.get('sender_id')).__name__})")
    print(f"   - sender_name: {msg.get('sender_name')}")
    print(f"   - content: {msg.get('content', '')[:50]}...")
    
    # Test de comparaison
    if msg.get('sender_id') == user.id:
        print(f"   ✅ sender_id == user.id (MATCH)")
    else:
        print(f"   ❌ sender_id != user.id (NO MATCH)")
        print(f"      {msg.get('sender_id')} != {user.id}")

print("\n" + "=" * 70)
