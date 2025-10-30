# 💬 Système de Chat en Temps Réel - SmartCampus

## 🎯 Vue d'ensemble

Un système de forum/chat en temps réel complet pour SmartCampus utilisant Django Channels et WebSocket.

## ✨ Fonctionnalités

### Messages en temps réel
- ✅ Envoi et réception instantanés via WebSocket
- ✅ Pas de rechargement de page nécessaire
- ✅ Interface moderne et responsive

### Gestion des salons
- ✅ Salons publics (accessibles à tous)
- ✅ Salons de groupe (pour groupes spécifiques)
- ✅ Salons de cours (liés à des cours)
- ✅ Salons privés (1-to-1, à implémenter)

### Indicateurs de présence
- ✅ Voir qui est en ligne/hors ligne
- ✅ Indicateur "en train d'écrire..."
- ✅ Liste des participants en temps réel

### Historique et sauvegarde
- ✅ Tous les messages sont sauvegardés en base de données
- ✅ Historique consultable
- ✅ Soft delete des messages

## 🚀 Installation et Démarrage

### Prérequis

1. **Redis doit être installé et en cours d'exécution**

**Windows:**
```powershell
# Télécharger Redis pour Windows depuis:
# https://github.com/microsoftarchive/redis/releases
# Ou utiliser WSL:
wsl
sudo apt-get install redis-server
redis-server
```

**Linux/Mac:**
```bash
# Installation
sudo apt-get install redis-server  # Debian/Ubuntu
brew install redis                  # Mac

# Démarrage
redis-server
```

2. **Packages Python installés** (déjà fait)
```bash
pip install channels channels-redis daphne
```

### Démarrage du serveur

1. **Démarrer Redis** (dans un terminal séparé)
```powershell
redis-server
```

2. **Démarrer le serveur Django** (avec Daphne pour ASGI)
```powershell
cd C:\Users\taher\OneDrive\Desktop\Django\SmartCampus
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Le serveur utilisera automatiquement Daphne (serveur ASGI) au lieu de Gunicorn.

## 📝 Utilisation

### Accéder au Chat

1. **Se connecter** à SmartCampus
2. **Aller sur** : http://127.0.0.1:8000/chat/
3. **Choisir un salon** ou en créer un nouveau
4. **Commencer à discuter** !

### URLs principales

- `/chat/` - Liste des salons
- `/chat/room/<slug>/` - Interface de chat
- `/chat/create/` - Créer un nouveau salon

### WebSocket

- `ws://127.0.0.1:8000/ws/chat/<slug>/` - Connexion WebSocket

## 🏗️ Architecture

### Structure des fichiers

```
chat/
├── models.py              # ChatRoom, ChatMessage, ChatParticipant
├── consumers.py           # WebSocket consumer
├── routing.py             # WebSocket routing
├── views.py               # Vues Django (HTTP)
├── urls.py                # URLs HTTP
├── admin.py               # Interface admin
├── templates/
│   └── chat/
│       ├── room_list.html      # Liste des salons
│       ├── chat_room.html      # Interface de chat
│       └── create_room.html    # Création de salon
└── static/
    └── chat/
        └── js/
            └── chat.js         # Logique WebSocket client
```

### Flow de données

```
Client (Browser)
    ↓ WebSocket
Consumer (Django Channels)
    ↓ Channel Layer (Redis)
All Clients in Room
    ↓ Database (SQLite)
Message History
```

## 🔧 Configuration

### Settings Django

```python
INSTALLED_APPS = [
    'daphne',  # DOIT ÊTRE EN PREMIER
    ...
    'channels',
    'chat',
]

ASGI_APPLICATION = 'smartcampus.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}
```

### Variables d'environnement (.env)

```env
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 📊 Modèles de données

### ChatRoom
- `name` - Nom du salon
- `slug` - Identifiant URL unique
- `room_type` - Type (public, private, course, group)
- `description` - Description
- `created_by` - Créateur
- `participants` - Utilisateurs membres

### ChatMessage
- `room` - Salon
- `sender` - Expéditeur
- `content` - Contenu du message
- `timestamp` - Horodatage
- `is_edited` - Marqueur d'édition
- `is_deleted` - Soft delete

### ChatParticipant
- `room` - Salon
- `user` - Utilisateur
- `is_online` - Statut en ligne
- `last_seen` - Dernière activité
- `unread_count` - Messages non lus

## 🎨 Interface utilisateur

### Design
- **Bootstrap 5** pour le style
- **Bootstrap Icons** pour les icônes
- **Dégradés modernes** pour un look professionnel
- **Animations CSS** pour les messages
- **Responsive** - fonctionne sur mobile et desktop

### Couleurs
- Primaire: Dégradé violet (#667eea → #764ba2)
- En ligne: Vert (#28a745)
- Hors ligne: Gris (#6c757d)

## 🔒 Sécurité

- ✅ Authentification requise (login_required)
- ✅ Validation des permissions par salon
- ✅ Protection CSRF
- ✅ Échappement HTML des messages
- ✅ AllowedHostsOriginValidator pour WebSocket

## 🐛 Dépannage

### Redis ne démarre pas
```bash
# Vérifier le port
netstat -an | findstr 6379

# Redémarrer Redis
redis-cli shutdown
redis-server
```

### WebSocket ne se connecte pas
1. Vérifier que Redis est en cours d'exécution
2. Vérifier les logs du serveur Django
3. Vérifier la console du navigateur (F12)

### Messages ne s'affichent pas
1. Vérifier la connexion WebSocket (console)
2. Vérifier que l'utilisateur est authentifié
3. Vérifier les permissions du salon

## 📈 Évolutions futures

### Court terme
- [ ] Édition de messages
- [ ] Suppression de messages
- [ ] Réactions (emojis)
- [ ] Notifications push

### Moyen terme
- [ ] Partage de fichiers/images
- [ ] Messages privés 1-to-1
- [ ] Recherche dans l'historique
- [ ] Formatage de texte (markdown)

### Long terme
- [ ] Appels vidéo/audio (WebRTC)
- [ ] Partage d'écran
- [ ] Intégration IA (chatbot)
- [ ] Traduction automatique

## 🧪 Tests

### Tester le chat

1. **Ouvrir deux navigateurs** (ou deux onglets en navigation privée)
2. **Se connecter avec deux utilisateurs différents**
3. **Rejoindre le même salon**
4. **Envoyer des messages** - ils apparaîtront en temps réel

### Créer des utilisateurs de test

```python
python manage.py shell

from django.contrib.auth.models import User
User.objects.create_user('user1', 'user1@test.com', 'password123')
User.objects.create_user('user2', 'user2@test.com', 'password123')
```

## 📚 Ressources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)

## 🎉 Félicitations !

Vous avez maintenant un système de chat en temps réel complet pour SmartCampus ! 🚀💬

---

**Créé le:** 29 Octobre 2025  
**Version:** 1.0.0  
**Auteur:** SmartCampus Team
