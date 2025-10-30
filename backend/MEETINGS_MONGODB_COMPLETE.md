# 🎥 Système de Visioconférence - MongoDB Backend

## ✅ IMPLÉMENTATION COMPLÈTE

Le système de visioconférence utilise maintenant **MongoDB avec l'architecture du backend** !

---

## 🏗️ Architecture Backend

### Structure créée

```
backend/meetings/
├── __init__.py           ✅ Module initialization
├── models.py             ✅ MongoDB models (Meeting + MeetingParticipant)
├── views.py              ✅ API REST avec DRF
├── urls.py               ✅ Routes API
└── MEETINGS_API.md       ✅ Documentation complète
```

### Intégration

```python
# backend/config/urls.py
urlpatterns = [
    ...
    path('api/meetings/', include('meetings.urls')),  # ✅ Ajouté
]
```

---

## 📊 Modèles MongoDB

### 1. Meeting Model
```python
class Meeting:
    COLLECTION_NAME = 'meetings'
    
    # Fields
    - _id (ObjectId)
    - meeting_id (UUID) - Unique identifier for Jitsi
    - title (string)
    - description (string)
    - instructor_id (ObjectId) - Reference to users collection
    - instructor_email (string)
    - scheduled_date (datetime)
    - duration (int) - minutes
    - meeting_link (string) - Auto-generated Jitsi URL
    - status (enum) - scheduled, ongoing, completed, cancelled
    - started_at (datetime|null)
    - ended_at (datetime|null)
    - created_at (datetime)
    - updated_at (datetime)
```

**Méthodes** :
- `create(**kwargs)` - Créer une réunion
- `find_by_id(meeting_id)` - Trouver par ID
- `find_by_instructor(instructor_id)` - Réunions d'un instructeur
- `update(meeting_id, **kwargs)` - Modifier
- `delete(meeting_id)` - Annuler (soft delete)
- `start_meeting(meeting_id)` - Démarrer
- `end_meeting(meeting_id)` - Terminer

### 2. MeetingParticipant Model
```python
class MeetingParticipant:
    COLLECTION_NAME = 'meeting_participants'
    
    # Fields
    - _id (ObjectId)
    - meeting_id (ObjectId) - Reference to meetings
    - student_id (ObjectId) - Reference to users
    - student_email (string)
    - status (enum) - invited, accepted, declined, attended, absent
    - joined_at (datetime|null)
    - left_at (datetime|null)
    - created_at (datetime)
    - updated_at (datetime)
```

**Méthodes** :
- `create(**kwargs)` - Ajouter participant
- `find_by_meeting(meeting_id)` - Participants d'une réunion
- `find_by_student(student_id)` - Réunions d'un étudiant
- `update_status(meeting_id, student_id, status)` - Changer statut
- `mark_attended(meeting_id, student_id)` - Marquer présent
- `mark_left(meeting_id, student_id)` - Marquer sorti
- `get_duration(meeting_id, student_id)` - Calculer durée

---

## 🔐 Vérification du rôle

### Dans les vues
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def meeting_create(request):
    user_role = request.user.get('role', 'student')
    
    # Only instructors can create meetings
    if user_role != 'instructor':
        return Response({
            'success': False,
            'error': 'Only instructors can create meetings'
        }, status=403)
    
    # Create meeting...
```

### Permissions

| Action | Student (`role='student'`) | Instructor (`role='instructor'`) |
|--------|---------------------------|----------------------------------|
| Créer réunion | ❌ | ✅ |
| Voir ses réunions | ✅ (invitations) | ✅ (créées) |
| Modifier réunion | ❌ | ✅ (ses réunions) |
| Annuler réunion | ❌ | ✅ (ses réunions) |
| Démarrer réunion | ❌ | ✅ (ses réunions) |
| Terminer réunion | ❌ | ✅ (ses réunions) |
| Rejoindre réunion | ✅ (si invité) | ✅ (ses réunions) |
| Accepter/Refuser | ✅ (si invité) | N/A |

---

## 🌐 API Endpoints

### Base URL
```
http://localhost:8001/api/meetings/
```

### Endpoints principaux

1. **`GET /api/meetings/`** - Liste des réunions
   - Instructeur : Ses réunions créées
   - Étudiant : Ses invitations

2. **`POST /api/meetings/`** - Créer réunion (instructeur uniquement)
   ```json
   {
     "title": "Cours Python",
     "description": "...",
     "scheduled_date": "2025-11-01T14:00:00",
     "duration": 60,
     "student_ids": ["id1", "id2"]
   }
   ```

3. **`GET /api/meetings/<id>/`** - Détails réunion

4. **`PUT /api/meetings/<id>/`** - Modifier réunion (instructeur)

5. **`DELETE /api/meetings/<id>/`** - Annuler réunion (instructeur)

6. **`POST /api/meetings/<id>/start/`** - Démarrer (instructeur)

7. **`POST /api/meetings/<id>/end/`** - Terminer (instructeur)

8. **`POST /api/meetings/<id>/join/`** - Rejoindre

9. **`POST /api/meetings/<id>/leave/`** - Quitter

10. **`POST /api/meetings/<id>/respond/`** - Accepter/Refuser
    ```json
    { "action": "accept" }  // or "decline"
    ```

11. **`GET /api/meetings/my/invitations/`** - Invitations étudiant

---

## 🔄 Workflow complet

### 1. Instructeur crée réunion
```bash
POST /api/meetings/
Authorization: Bearer <instructor_token>
{
  "title": "Machine Learning Basics",
  "scheduled_date": "2025-11-02T10:00:00",
  "duration": 90,
  "student_ids": ["student_id_1", "student_id_2"]
}

# Réponse
{
  "success": true,
  "meeting": {
    "id": "...",
    "meeting_link": "https://meet.jit.si/SmartCampus-<uuid>"
  }
}
```

### 2. Étudiant voit invitation
```bash
GET /api/meetings/my/invitations/
Authorization: Bearer <student_token>

# Réponse
{
  "meetings": [
    {
      "id": "...",
      "title": "Machine Learning Basics",
      "participant_status": "invited"
    }
  ]
}
```

### 3. Étudiant accepte
```bash
POST /api/meetings/<id>/respond/
{
  "action": "accept"
}

# Status devient "accepted"
```

### 4. Instructeur démarre
```bash
POST /api/meetings/<id>/start/

# Status devient "ongoing"
```

### 5. Étudiant rejoint
```bash
POST /api/meetings/<id>/join/

# Réponse
{
  "meeting_link": "https://meet.jit.si/SmartCampus-<uuid>"
}

# Participant status devient "attended"
# joined_at enregistré
```

### 6. Instructeur termine
```bash
POST /api/meetings/<id>/end/

# Status devient "completed"
# ended_at enregistré
```

---

## 💾 Collections MongoDB

### `meetings`
Stocke toutes les réunions.

**Index recommandés** :
```javascript
db.meetings.createIndex({ instructor_id: 1, status: 1 })
db.meetings.createIndex({ scheduled_date: 1 })
db.meetings.createIndex({ meeting_id: 1 })
```

### `meeting_participants`
Stocke les participants et leur présence.

**Index recommandés** :
```javascript
db.meeting_participants.createIndex({ meeting_id: 1 })
db.meeting_participants.createIndex({ student_id: 1 })
db.meeting_participants.createIndex({ meeting_id: 1, student_id: 1 }, { unique: true })
```

---

## 🔗 Connexion Frontend ↔ Backend

### Configuration Frontend
```javascript
// Dans le frontend
const API_URL = 'http://localhost:8001/api/meetings/'

// Créer réunion (instructeur)
fetch(API_URL, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Cours Python',
    scheduled_date: '2025-11-01T14:00:00',
    duration: 60,
    student_ids: ['id1', 'id2']
  })
})
```

### CORS Configuration
```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',  # Frontend
    'http://127.0.0.1:8000',
]
```

---

## 🧪 Tests

### 1. Créer utilisateur instructeur
```bash
POST http://localhost:8001/api/users/register/
{
  "email": "prof@test.com",
  "username": "prof1",
  "password": "password123",
  "role": "instructor"
}
```

### 2. Créer étudiants
```bash
POST http://localhost:8001/api/users/register/
{
  "email": "student1@test.com",
  "username": "student1",
  "password": "password123",
  "role": "student"
}
```

### 3. Login instructeur
```bash
POST http://localhost:8001/api/users/login/
{
  "email": "prof@test.com",
  "password": "password123"
}

# Récupérer le token
```

### 4. Créer réunion
```bash
POST http://localhost:8001/api/meetings/
Authorization: Bearer <instructor_token>
{
  "title": "Test Meeting",
  "scheduled_date": "2025-11-01T14:00:00",
  "duration": 60,
  "student_ids": ["<student_id>"]
}
```

### 5. Login étudiant et voir invitations
```bash
POST http://localhost:8001/api/users/login/
{
  "email": "student1@test.com",
  "password": "password123"
}

GET http://localhost:8001/api/meetings/my/invitations/
Authorization: Bearer <student_token>
```

---

## 📝 Différences avec le frontend principal

### Frontend SmartCampus (port 8000)
- Utilise Django templates
- Base de données : SQLite pour auth, MongoDB pour chat
- Interface utilisateur complète

### Backend API (port 8001)
- API REST pure avec DRF
- MongoDB pour tout (users, courses, meetings)
- Pas de templates, seulement JSON

### Solution hybride possible
1. **Frontend** appelle **Backend API** pour les meetings
2. Frontend affiche les données via AJAX/fetch
3. Authentification partagée via JWT

---

## 🎯 Avantages architecture MongoDB

✅ **Flexibilité** : Schéma JSON flexible
✅ **Performance** : Requêtes rapides avec index
✅ **Scalabilité** : Facile à scaler horizontalement
✅ **Cohérence** : Architecture backend cohérente (tout en MongoDB)
✅ **Intégration** : Facile à intégrer avec chat existant

---

## 🚀 Prochaines étapes

### Option 1 : Frontend pur Django (actuel)
Garder le système meetings dans le frontend principal avec SQLite.

**Avantages** :
- Déjà implémenté et fonctionnel
- Interface complète avec templates
- Pas besoin d'API calls

**Inconvénients** :
- Base de données différente (SQLite vs MongoDB)
- Pas de cohérence avec le backend

### Option 2 : Migrer vers backend API
Utiliser le backend MongoDB et faire des appels API depuis le frontend.

**Avantages** :
- Architecture cohérente (tout en MongoDB)
- API réutilisable (apps mobiles, etc.)
- Séparation frontend/backend

**Inconvénients** :
- Besoin de réécrire frontend en AJAX/fetch
- Plus complexe à maintenir
- CORS à gérer

### Option 3 : Hybride (recommandé)
- Backend API pour la logique métier
- Frontend pour l'UI et l'affichage
- Communication via API calls

---

## 📖 Documentation complète

Voir **`MEETINGS_API.md`** pour la documentation complète de l'API.

---

## ✅ RÉSUMÉ

🎯 **Système créé avec succès** :
- ✅ Modèles MongoDB (Meeting + MeetingParticipant)
- ✅ API REST complète (11 endpoints)
- ✅ Vérification du rôle (`role='instructor'`)
- ✅ Permissions correctes
- ✅ Documentation API complète
- ✅ Integration avec architecture backend existante

**L'instructeur est bien celui qui crée les réunions !** 🎉
