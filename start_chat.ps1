# ==============================================================================
# Script de démarrage SIMPLE pour SmartCampus avec Chat
# SANS REDIS - Parfait pour le développement !
# ==============================================================================

Write-Host ""
Write-Host "🚀 Démarrage de SmartCampus avec Chat en Temps Réel" -ForegroundColor Green
Write-Host "   (Mode développement - Sans Redis)" -ForegroundColor Cyan
Write-Host ""

# Vérifier si dans le bon répertoire
if (-Not (Test-Path "manage.py")) {
    Write-Host "❌ Erreur: manage.py introuvable!" -ForegroundColor Red
    Write-Host "Assurez-vous d'être dans le répertoire SmartCampus" -ForegroundColor Yellow
    exit 1
}

# Activer l'environnement virtuel
Write-Host "🔧 Activation de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Environnement virtuel activé" -ForegroundColor Green
} else {
    Write-Host "❌ Environnement virtuel introuvable!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Appliquer les migrations
Write-Host "📦 Application des migrations..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'application des migrations" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Migrations appliquées" -ForegroundColor Green

Write-Host ""

# Collecter les fichiers statiques
Write-Host "📁 Collection des fichiers statiques..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear 2>$null
Write-Host "✅ Fichiers statiques collectés" -ForegroundColor Green

Write-Host ""

# Créer un salon par défaut
Write-Host "💬 Création du salon de chat par défaut..." -ForegroundColor Yellow
$output = python manage.py shell -c "from chat.models import ChatRoom; from django.contrib.auth.models import User; admin = User.objects.first(); room, created = ChatRoom.objects.get_or_create(slug='general', defaults={'name': 'General', 'room_type': 'public', 'description': 'Salon général', 'created_by': admin}) if admin else (None, False); print('created' if created else 'exists')" 2>$null

if ($output -match "created") {
    Write-Host "✅ Salon 'General' créé" -ForegroundColor Green
} else {
    Write-Host "✅ Salon 'General' existe déjà" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🎉 SmartCampus est prêt!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 URLs disponibles:" -ForegroundColor Yellow
Write-Host "  • Page d'accueil:    http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  • Chat (menu):       Cliquez sur 'Chat' dans le menu" -ForegroundColor White
Write-Host "  • Chat (direct):     http://127.0.0.1:8000/chat/" -ForegroundColor White
Write-Host "  • Salon General:     http://127.0.0.1:8000/chat/room/general/" -ForegroundColor White
Write-Host "  • Admin:             http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "✅ Chat en temps réel: ACTIVÉ (Backend en mémoire)" -ForegroundColor Green
Write-Host "   Note: Fonctionne pour 1 serveur, parfait pour le développement!" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Démarrage du serveur Django..." -ForegroundColor Yellow
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Gray
Write-Host ""

# Démarrer le serveur
python manage.py runserver
