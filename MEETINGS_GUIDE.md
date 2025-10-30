# 🎥 Système de Visioconférence - Guide de Continuation

## ✅ Ce qui a été fait

### 1. **Application créée**
- ✅ Application `meetings` créée
- ✅ Ajoutée à `INSTALLED_APPS` dans `settings.py`

### 2. **Modèles créés** (`meetings/models.py`)
- ✅ **Meeting** : Réunion avec titre, date, durée, lien Jitsi
- ✅ **MeetingParticipant** : Participants avec statut (invité, accepté, présent, etc.)
- ✅ Méthodes : `start_meeting()`, `end_meeting()`, `cancel_meeting()`
- ✅ Properties : `can_start`, `can_join`, `is_upcoming`, `is_past`

### 3. **Admin configuré** (`meetings/admin.py`)
- ✅ Interface admin complète avec badges colorés
- ✅ Actions : Démarrer, Terminer, Annuler
- ✅ Inline pour ajouter des participants
- ✅ Statistiques : nombre de participants, présents

### 4. **Base de données**
- ✅ Migrations créées et appliquées
- ✅ Tables : `meetings_meeting`, `meetings_meetingparticipant`

---

## 📋 Prochaines étapes

### Étape 1 : Créer les formulaires (`meetings/forms.py`)

```bash
Créez le fichier meetings/forms.py avec :
- MeetingForm : Formulaire de création/modification
- Widget datepicker pour scheduled_date
- Sélection multiple d'étudiants avec filtre
```

### Étape 2 : Créer les vues (`meetings/views.py`)

**Pour les instructeurs** :
- `meeting_list` - Liste des réunions
- `meeting_create` - Créer une réunion
- `meeting_detail` - Détails d'une réunion
- `meeting_update` - Modifier une réunion
- `meeting_delete` - Annuler une réunion
- `meeting_start` - Démarrer une réunion

**Pour les étudiants** :
- `student_meetings` - Mes invitations
- `meeting_join` - Rejoindre une réunion
- `meeting_respond` - Accepter/Refuser

### Étape 3 : Créer les URLs (`meetings/urls.py`)

```python
urlpatterns = [
    # Instructeur
    path('', views.meeting_list, name='meeting_list'),
    path('create/', views.meeting_create, name='meeting_create'),
    path('<uuid:pk>/', views.meeting_detail, name='meeting_detail'),
    path('<uuid:pk>/edit/', views.meeting_update, name='meeting_update'),
    path('<uuid:pk>/delete/', views.meeting_delete, name='meeting_delete'),
    path('<uuid:pk>/start/', views.meeting_start, name='meeting_start'),
    path('<uuid:pk>/end/', views.meeting_end, name='meeting_end'),
    
    # Étudiant
    path('my-meetings/', views.student_meetings, name='student_meetings'),
    path('<uuid:pk>/join/', views.meeting_join, name='meeting_join'),
    path('<uuid:pk>/respond/<str:action>/', views.meeting_respond, name='meeting_respond'),
]
```

### Étape 4 : Ajouter aux URLs principales

Dans `smartcampus/urls.py` :
```python
path('meetings/', include('meetings.urls')),
```

### Étape 5 : Créer les templates

Créer la structure :
```
meetings/templates/meetings/
├── base.html
├── meeting_list.html
├── meeting_create.html
├── meeting_detail.html
├── meeting_update.html
├── student_meetings.html
└── meeting_room.html (pour Jitsi intégré)
```

### Étape 6 : Créer les fichiers statiques

```
meetings/static/meetings/
├── css/
│   └── meetings.css
└── js/
    └── meetings.js
```

### Étape 7 : Intégration Jitsi Meet

Dans `meeting_room.html`, intégrer Jitsi :
```html
<script src='https://meet.jit.si/external_api.js'></script>
<script>
const domain = 'meet.jit.si';
const options = {
    roomName: '{{ meeting.meeting_id }}',
    width: '100%',
    height: 700,
    parentNode: document.querySelector('#meet'),
    userInfo: {
        displayName: '{{ user.get_full_name }}'
    }
};
const api = new JitsiMeetExternalAPI(domain, options);
</script>
```

---

## 🚀 Commandes pour continuer

### 1. Tester l'admin
```bash
python manage.py runserver
# Aller sur http://127.0.0.1:8000/admin/meetings/
```

### 2. Créer une réunion de test
Dans l'admin Django :
- Meetings → Add Meeting
- Remplir : titre, date future, instructeur
- Ajouter des participants

### 3. Vérifier la base de données
```bash
python manage.py shell
>>> from meetings.models import Meeting
>>> Meeting.objects.all()
>>> m = Meeting.objects.first()
>>> m.can_start
>>> m.meeting_link
```

---

## 📦 Prompt pour l'agent (suite)

**Maintenant, créez les fichiers suivants** :

1. **`meetings/forms.py`** :
   - MeetingForm avec validation de date future
   - Widget DateTimeInput avec datepicker
   - Champ students avec CheckboxSelectMultiple

2. **`meetings/views.py`** :
   - Toutes les vues pour instructeur et étudiant
   - Décorateurs @login_required
   - Permissions : seul l'instructeur peut modifier sa réunion

3. **`meetings/urls.py`** :
   - Routes pour toutes les vues

4. **Templates Bootstrap** :
   - Liste avec filtres (à venir/passées/toutes)
   - Formulaire avec datepicker
   - Page de détail avec bouton "Rejoindre"
   - Intégration Jitsi Meet

5. **Notifications (optionnel)** :
   - Signal post_save pour envoyer des emails
   - Créer `meetings/signals.py`

---

## 🎯 Fonctionnalités avancées (optionnelles)

- [ ] **Rappels automatiques** : Celery task pour envoyer un email 15min avant
- [ ] **Enregistrement vidéo** : Intégration Jitsi recording
- [ ] **Chat intégré** : Relier avec l'app chat existante
- [ ] **Calendrier** : Vue calendrier des réunions
- [ ] **API REST** : ViewSets DRF pour app mobile
- [ ] **WebRTC direct** : Agora.io au lieu de Jitsi
- [ ] **Sondages** : Créer des sondages pendant la réunion
- [ ] **Partage d'écran** : Intégré dans Jitsi
- [ ] **Breakout rooms** : Salles de sous-groupes

---

## 📝 Notes importantes

### Permissions
- Seuls les **instructeurs** peuvent créer des réunions
- Les **étudiants** ne voient que leurs invitations
- Vérifier `user.is_staff` ou créer un groupe "Instructeurs"

### Sécurité
- Valider que la date est dans le futur
- Vérifier que l'utilisateur est bien l'instructeur avant modification
- Limiter l'accès au lien de réunion aux participants invités

### Performance
- Index sur `scheduled_date` et `instructor` (déjà créés)
- Précharger les participants : `.select_related('instructor').prefetch_related('students')`

---

**Voulez-vous que je continue avec la création des formulaires et vues ?**
