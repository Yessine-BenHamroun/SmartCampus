# 🚀 Guide de Démarrage Rapide - Chat en Temps Réel

## ⚡ Installation Redis (Prérequis)

### Windows

**Option 1: Redis pour Windows**
1. Téléchargez: https://github.com/microsoftarchive/redis/releases
2. Extrayez le fichier ZIP
3. Exécutez `redis-server.exe`

**Option 2: WSL (Recommandé)**
```powershell
# Installer WSL
wsl --install

# Dans WSL
sudo apt-get update
sudo apt-get install redis-server

# Démarrer Redis
redis-server
```

### Vérifier que Redis fonctionne
```powershell
redis-cli ping
# Réponse attendue: PONG
```

## 🎯 Démarrage en 3 étapes

### 1. Démarrer Redis
```powershell
# Dans un terminal séparé
redis-server
```

Laissez ce terminal ouvert !

### 2. Démarrer Django
```powershell
cd C:\Users\taher\OneDrive\Desktop\Django\SmartCampus
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

### 3. Tester le Chat
1. Ouvrez: http://127.0.0.1:8000/chat/
2. Cliquez sur le salon "General"
3. Envoyez un message !

## 🧪 Test Multi-utilisateurs

### Méthode 1: Deux navigateurs différents
1. Ouvrez Chrome avec votre compte
2. Ouvrez Firefox avec un autre compte
3. Rejoignez le même salon
4. Discutez en temps réel !

### Méthode 2: Navigation privée
1. Ouvrez une fenêtre normale
2. Ouvrez une fenêtre de navigation privée
3. Connectez-vous avec deux comptes différents
4. Testez le chat !

## ✅ Checklist de vérification

- [ ] Redis est installé et démarré
- [ ] Port 6379 est disponible
- [ ] Django runserver est lancé
- [ ] Page /chat/ s'affiche correctement
- [ ] Salon "General" existe
- [ ] Messages s'affichent en temps réel

## 🐛 Problèmes courants

### Redis ne démarre pas
```powershell
# Vérifier si le port est utilisé
netstat -ano | findstr :6379

# Tuer le processus si nécessaire
taskkill /PID <PID> /F

# Redémarrer Redis
redis-server
```

### WebSocket Error 1006
- **Cause:** Redis n'est pas démarré
- **Solution:** Démarrer Redis

### Page 404 sur /chat/
- **Cause:** Migrations non appliquées
- **Solution:** `python manage.py migrate`

## 📝 Commandes utiles

```powershell
# Vérifier Redis
redis-cli ping

# Voir les migrations
python manage.py showmigrations chat

# Créer un superuser
python manage.py createsuperuser

# Accéder à l'admin
# http://127.0.0.1:8000/admin/

# Voir les salons dans l'admin
# http://127.0.0.1:8000/admin/chat/chatroom/
```

## 🎉 Prêt à utiliser !

Votre système de chat en temps réel est maintenant opérationnel ! 🚀💬

### Prochaines étapes
1. Créez plus de salons de discussion
2. Invitez des utilisateurs
3. Testez les fonctionnalités
4. Personnalisez le design

---

**Besoin d'aide ?** Consultez CHAT_DOCUMENTATION.md pour plus de détails.
