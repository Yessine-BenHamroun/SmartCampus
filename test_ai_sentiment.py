"""
Script de test pour l'analyseur de sentiment AI
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')
django.setup()

from chat.ai_sentiment import get_sentiment_analyzer

print("🚀 Test de l'analyseur de sentiment AI\n")
print("⏳ Chargement du modèle (première fois, cela peut prendre quelques secondes)...\n")

# Créer l'analyseur
analyzer = get_sentiment_analyzer()

# Messages de test
test_messages = [
    "This chat system is amazing! I love it!",
    "This is terrible and frustrating.",
    "The meeting is scheduled for tomorrow.",
    "Great work everyone! 🎉",
    "I'm not sure about this..."
]

print("=" * 60)
print("RÉSULTATS DE L'ANALYSE")
print("=" * 60)

for i, message in enumerate(test_messages, 1):
    result = analyzer.analyze_message(message)
    print(f"\n{i}. Message: \"{message}\"")
    print(f"   Sentiment: {result['sentiment']} {result['emoji']}")
    print(f"   Score: {result['score']:.2%}")
    print(f"   Confiance: {'Élevée' if result['score'] > 0.8 else 'Moyenne' if result['score'] > 0.6 else 'Faible'}")

print("\n" + "=" * 60)
print("✅ Test terminé avec succès!")
print("=" * 60)
