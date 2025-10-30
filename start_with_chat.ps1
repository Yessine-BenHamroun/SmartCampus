# ==============================================================================
# Script de démarrage pour SmartCampus avec Chat en Temps Réel
# ==============================================================================

Write-Host "🚀 Démarrage de SmartCampus avec Chat en Temps Réel..." -ForegroundColor Green
Write-Host ""

# Vérifier si dans le bon répertoire
if (-Not (Test-Path "manage.py")) {
    Write-Host "❌ Erreur: manage.py introuvable!" -ForegroundColor Red
    Write-Host "Assurez-vous d'être dans le répertoire SmartCampus" -ForegroundColor Yellow
    exit 1
}

Write-Host "📍 Répertoire de travail: $PWD" -ForegroundColor Cyan
Write-Host ""

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

# Vérifier Redis
Write-Host "🔍 Vérification de Redis..." -ForegroundColor Yellow
$redisRunning = $false

try {
    $redisTest = redis-cli ping 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis est déjà en cours d'exécution" -ForegroundColor Green
        $redisRunning = $true
    }
} catch {
    Write-Host "⚠️  Redis n'est pas en cours d'exécution" -ForegroundColor Yellow
}

if (-Not $redisRunning) {
    Write-Host ""
    Write-Host "❗ Redis doit être démarré pour le chat en temps réel" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pour installer Redis:" -ForegroundColor Cyan
    Write-Host "  1. Windows: Télécharger depuis https://github.com/microsoftarchive/redis/releases" -ForegroundColor White
    Write-Host "  2. WSL: wsl → sudo apt-get install redis-server" -ForegroundColor White
    Write-Host ""
    Write-Host "Pour démarrer Redis:" -ForegroundColor Cyan
    Write-Host "  • Dans un terminal séparé, exécutez: redis-server" -ForegroundColor White
    Write-Host "  • Ou avec WSL: wsl redis-server" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Voulez-vous continuer sans Redis? (o/n) [Le chat ne fonctionnera pas]"
    if ($choice -ne "o") {
        Write-Host "❌ Arrêt du script" -ForegroundColor Red
        exit 1
    }
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

# Créer un salon par défaut si inexistant
Write-Host "💬 Vérification du salon de chat par défaut..." -ForegroundColor Yellow
python manage.py shell -c "from chat.models import ChatRoom; from django.contrib.auth.models import User; admin = User.objects.first(); room, created = ChatRoom.objects.get_or_create(slug='general', defaults={'name': 'General', 'room_type': 'public', 'description': 'Salon général', 'created_by': admin}) if admin else (None, False); print('✅ Salon General ' + ('créé' if created else 'existe déjà'))"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🎉 SmartCampus est prêt!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 URLs disponibles:" -ForegroundColor Yellow
Write-Host "  • Page d'accueil:    http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  • Chat (salons):     http://127.0.0.1:8000/chat/" -ForegroundColor White
Write-Host "  • Salon General:     http://127.0.0.1:8000/chat/room/general/" -ForegroundColor White
Write-Host "  • Admin:             http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""

if ($redisRunning) {
    Write-Host "✅ Chat en temps réel: ACTIVÉ" -ForegroundColor Green
} else {
    Write-Host "⚠️  Chat en temps réel: DÉSACTIVÉ (Redis non démarré)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Démarrage du serveur Django..." -ForegroundColor Yellow
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Gray
Write-Host ""

# Démarrer le serveur
python manage.py runserver
