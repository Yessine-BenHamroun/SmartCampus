# 🔄 Intégration MongoDB pour la sélection des étudiants

## ✅ Modification effectuée

Le système de réunions récupère maintenant **les étudiants depuis MongoDB** au lieu de SQLite Django !

---

## 🎯 Problème résolu

### Avant (❌)
```python
# Récupérait les utilisateurs depuis Django/SQLite
students = forms.ModelMultipleChoiceField(
    queryset=User.objects.filter(is_staff=False),  # ❌ SQLite
    ...
)
```

**Problème** : Les utilisateurs sont stockés dans MongoDB, pas dans Django/SQLite.

### Après (✅)
```python
# Récupère les utilisateurs depuis MongoDB
db = get_db()
students_mongo = list(db.users.find({'role': 'student', 'is_active': True}))

# Crée les choix pour le formulaire
for student in students_mongo:
    email = student.get('email', '')
    first_name = student.get('first_name', '')
    last_name = student.get('last_name', '')
    
    label = f"{first_name} {last_name} ({email})"
    student_choices.append((email, label))
```

**Solution** : Requête MongoDB pour récupérer les utilisateurs avec `role='student'`.

---

## 🔍 Comment ça fonctionne

### 1. Connexion MongoDB

```python
from Learner.models import get_db

db = get_db()  # Connexion à la base MongoDB
```

### 2. Requête pour les étudiants

```python
students_mongo = list(db.users.find({
    'role': 'student',      # Seulement les étudiants
    'is_active': True       # Seulement les actifs
}))
```

### 3. Création des choix du formulaire

```python
student_choices = []
self.students_map = {}  # Map email -> User Django

for student in students_mongo:
    email = student.get('email', '')
    username = student.get('username', '')
    first_name = student.get('first_name', '')
    last_name = student.get('last_name', '')
    
    # Label lisible : "Taher Ben Ismail (benismail.taher@esprit.tn)"
    label = f"{first_name} {last_name}".strip()
    if email:
        label += f" ({email})"
    
    student_choices.append((email, label))
    
    # Créer/récupérer User Django correspondant (pour compatibilité)
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username or email.split('@')[0],
            'first_name': first_name,
            'last_name': last_name,
        }
    )
    self.students_map[email] = user
```

### 4. Sauvegarde

```python
def save(self, commit=True):
    # ...
    
    # Convertir les emails en objets User Django
    student_emails = self.cleaned_data.get('students')
    students = [self.students_map[email] for email in student_emails]
    
    for student in students:
        MeetingParticipant.objects.create(
            meeting=meeting,
            student=student,
            status='invited'
        )
```

---

## 📋 Fichiers modifiés

### 1. `meetings/forms.py`

**MeetingForm** (création de réunion) :
```python
class MeetingForm(forms.ModelForm):
    students = forms.MultipleChoiceField(  # ✅ MultipleChoiceField au lieu de ModelMultipleChoiceField
        widget=forms.CheckboxSelectMultiple,
        ...
    )
    
    def __init__(self, *args, **kwargs):
        # ✅ Récupère les étudiants depuis MongoDB
        db = get_db()
        students_mongo = list(db.users.find({'role': 'student', 'is_active': True}))
        
        # ✅ Crée les choix dynamiquement
        student_choices = [(email, label), ...]
        self.fields['students'].choices = student_choices
```

**MeetingUpdateForm** (modification de réunion) :
- Même système que `MeetingForm`
- Pré-sélectionne les étudiants déjà invités

### 2. `meetings/views.py`

**meeting_update()** :
```python
# ✅ Convertit les emails en User Django
student_emails = form.cleaned_data.get('students')
students = [form.students_map[email] for email in student_emails]

for student in students:
    MeetingParticipant.objects.create(meeting=meeting, student=student, status='invited')
```

---

## 🎨 Affichage dans le formulaire

### Exemple de rendu

```
☐ Tout sélectionner    ☐ Tout désélectionner

Étudiants à inviter:

☐ Taher Ben Ismail (benismail.taher@esprit.tn)
☐ Ahmed Mohamed (ahmed.mohamed@esprit.tn)
☐ Sarah Tounsi (sarah.tounsi@esprit.tn)
☐ Ali Ben Ali (ali.benali@esprit.tn)
```

**Format** : `{first_name} {last_name} ({email})`

---

## 🔄 Synchronisation Django ↔ MongoDB

### Pourquoi créer des User Django ?

Bien que les utilisateurs soient dans MongoDB, le modèle `Meeting` utilise des `ForeignKey` Django :

```python
class Meeting(models.Model):
    instructor = models.ForeignKey(User, ...)  # Django User
    students = models.ManyToManyField(User, ...)  # Django User
```

**Solution** : Créer automatiquement les User Django correspondants

```python
user, created = User.objects.get_or_create(
    email=email,
    defaults={
        'username': username or email.split('@')[0],
        'first_name': first_name,
        'last_name': last_name,
    }
)
```

### Avantages

✅ **Compatibilité** : Les modèles Django continuent de fonctionner
✅ **Source de vérité** : MongoDB reste la source principale
✅ **Synchronisation** : User Django créé automatiquement au besoin

---

## 🧪 Test

### Scénario : Créer une réunion

1. **Connexion en tant qu'instructeur** (`role='instructor'`)
2. **Accéder à** `http://127.0.0.1:8000/meetings/create/`
3. **Voir la liste des étudiants** :
   - Tous les utilisateurs avec `role='student'` dans MongoDB
   - Affichage : "Prénom Nom (email)"
   - Checkboxes pour sélection multiple
4. **Sélectionner des étudiants**
5. **Enregistrer**
6. **Vérification** :
   - Réunion créée dans SQLite (table `meetings_meeting`)
   - Participants créés (table `meetings_meetingparticipant`)
   - User Django créés si nécessaire (table `auth_user`)

### Base de données MongoDB

```javascript
// Requête MongoDB exécutée
db.users.find({
  role: 'student',
  is_active: true
})

// Exemple de résultat
{
  _id: ObjectId('690289cda319f8de28221956'),
  email: 'benismail.taher@esprit.tn',
  username: 'benismailtaher',
  first_name: 'Taher',
  last_name: 'Ben Ismail',
  role: 'student',  // ← Critère de filtrage
  is_active: true   // ← Critère de filtrage
}
```

---

## 📊 Flux de données complet

```
1. Instructeur crée une réunion
   └─> Form.__init__()
       └─> MongoDB.find({'role': 'student'})
           └─> Liste des étudiants MongoDB
               └─> Création des choix du formulaire
                   └─> Affichage des checkboxes

2. Instructeur sélectionne des étudiants
   └─> Form.clean_students()
       └─> Validation (au moins 1 étudiant)

3. Formulaire soumis
   └─> Form.save()
       └─> Conversion emails → User Django
           └─> Création User Django si nécessaire
               └─> Création MeetingParticipant
                   └─> SQLite : meeting_participants table

4. Étudiants voient leurs invitations
   └─> student_meetings view
       └─> MeetingParticipant.objects.filter(student=request.user)
```

---

## ⚙️ Configuration requise

### MONGODB_SETTINGS

```python
# smartcampus/settings.py
MONGODB_SETTINGS = {
    'host': 'mongodb://localhost:27017/',
    'db_name': 'smartcampus',
}
```

### Collection users

```javascript
// Structure attendue
{
  _id: ObjectId,
  email: string,
  username: string,
  first_name: string,
  last_name: string,
  role: 'student' | 'instructor' | 'admin',  // ← Important !
  is_active: boolean,
  ...
}
```

---

## 🎯 Avantages de cette approche

### 1. Source unique de vérité
✅ MongoDB contient tous les utilisateurs
✅ Pas de duplication de données

### 2. Cohérence avec le backend
✅ Même logique que le backend API
✅ Utilise le champ `role` MongoDB

### 3. Mise à jour automatique
✅ Nouveaux étudiants apparaissent automatiquement
✅ Pas besoin de synchronisation manuelle

### 4. Performance
✅ Une seule requête MongoDB au chargement du formulaire
✅ Pas de requêtes répétées

### 5. Compatibilité
✅ Fonctionne avec les modèles Django existants
✅ Pas besoin de réécrire tout le système

---

## 🚀 Prochaines améliorations possibles

### 1. Recherche/Filtre d'étudiants
```python
# Ajouter un champ de recherche
search = forms.CharField(required=False, label="Rechercher un étudiant")
```

### 2. Groupes d'étudiants
```python
# Permettre la sélection par groupe/classe
class_filter = forms.ChoiceField(choices=[('all', 'Tous'), ...])
```

### 3. Sélection rapide
```javascript
// Boutons JavaScript
- Tout sélectionner
- Tout désélectionner
- Inverser la sélection
```

### 4. Affichage amélioré
```html
<!-- Avec photos de profil -->
<label>
  <input type="checkbox" value="email">
  <img src="{{ student.profile_image }}">
  {{ student.first_name }} {{ student.last_name }}
</label>
```

---

## ✅ Checklist de vérification

- [x] Récupération des étudiants depuis MongoDB
- [x] Filtrage par `role='student'`
- [x] Filtrage par `is_active=True`
- [x] Affichage avec nom complet et email
- [x] Création automatique User Django
- [x] Validation (au moins 1 étudiant)
- [x] Sauvegarde des participants
- [x] Formulaire de modification (MeetingUpdateForm)
- [x] Pré-sélection des étudiants existants

---

## 🎉 Résultat

**Maintenant, le système affiche uniquement les utilisateurs avec `role='student'` depuis MongoDB !**

L'instructeur voit la liste complète et à jour des étudiants actifs dans la base MongoDB. 🚀
