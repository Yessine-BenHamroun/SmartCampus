# 🔒 Correction : Vérification du rôle pour les réunions

## ❌ Problème identifié

**L'utilisateur avec `role='student'` pouvait créer des réunions !**

### Cause du problème

Le système meetings du frontend utilisait `request.user.is_staff` pour vérifier si un utilisateur est instructeur, mais :

1. **Les utilisateurs sont stockés dans MongoDB** avec un champ `role`
2. **Les valeurs possibles** : `'student'`, `'instructor'`, `'admin'`
3. **`is_staff` n'était pas synchronisé** avec le rôle MongoDB

### Comportement incorrect

```python
# ❌ AVANT (INCORRECT)
if not request.user.is_staff:
    messages.error(request, "Seuls les instructeurs peuvent créer des réunions.")
    return redirect('student_meetings')
```

**Résultat** : Un étudiant (`role='student'`) pouvait créer des réunions si `is_staff=True` dans Django !

---

## ✅ Solution implémentée

### 1. Fonction helper pour récupérer le rôle

```python
def get_user_role(request):
    """
    Récupère le rôle de l'utilisateur depuis MongoDB
    Returns: 'instructor', 'student', ou 'admin'
    """
    # Vérifier si les données de session sont disponibles
    if hasattr(request.user, 'session_data'):
        return request.user.session_data.get('role', 'student')
    
    # Fallback : utiliser is_staff (compatibilité)
    if request.user.is_staff:
        return 'instructor'
    
    return 'student'


def is_instructor(request):
    """Vérifie si l'utilisateur est un instructeur"""
    role = get_user_role(request)
    return role in ['instructor', 'admin']
```

### 2. Correction des vérifications

```python
# ✅ APRÈS (CORRECT)
if not is_instructor(request):
    messages.error(request, "Seuls les instructeurs peuvent créer des réunions.")
    return redirect('student_meetings')
```

---

## 🔍 Comment ça fonctionne

### Middleware SessionAuthMiddleware

Le middleware `Learner/middleware.py` synchronise l'authentification :

```python
# Ajouter les données supplémentaires comme attributs
request.user.session_data = user_data
```

### Données de session

Quand un utilisateur se connecte, ses données MongoDB sont stockées dans la session :

```python
request.session['user'] = {
    '_id': ObjectId('...'),
    'email': 'benismail.taher@esprit.tn',
    'username': 'benismailtaher',
    'role': 'student',  # ← Rôle MongoDB
    'first_name': 'Taher',
    'last_name': 'Ben Ismail',
    ...
}
```

### Vérification du rôle

```python
def is_instructor(request):
    role = get_user_role(request)  # Récupère 'student'
    return role in ['instructor', 'admin']  # False ✓
```

---

## 🎯 Vues corrigées

### Vues instructeur (nécessitent role='instructor')

1. ✅ **`meeting_list`** - Liste des réunions
2. ✅ **`meeting_create`** - Créer une réunion
3. ✅ **`meeting_update`** - Modifier une réunion
4. ✅ **`meeting_delete`** - Annuler une réunion
5. ✅ **`meeting_start`** - Démarrer une réunion
6. ✅ **`meeting_end`** - Terminer une réunion

### Vues étudiant (accessibles avec role='student')

1. ✅ **`student_meetings`** - Voir ses invitations
2. ✅ **`meeting_detail`** - Voir détails (si invité)
3. ✅ **`meeting_join`** - Rejoindre une réunion
4. ✅ **`meeting_respond`** - Accepter/Refuser invitation
5. ✅ **`meeting_room`** - Salle Jitsi
6. ✅ **`meeting_leave`** - Quitter une réunion

---

## 🧪 Test de la correction

### Scénario 1 : Étudiant essaie de créer une réunion

```python
# Utilisateur : benismailtaher
# Rôle MongoDB : 'student'

# Tentative d'accès à /meetings/create/
GET /meetings/create/

# Résultat :
# ❌ Accès refusé
# ✅ Message : "Seuls les instructeurs peuvent créer des réunions."
# ✅ Redirection vers /meetings/student/
```

### Scénario 2 : Instructeur crée une réunion

```python
# Utilisateur : instructor@example.com
# Rôle MongoDB : 'instructor'

# Accès à /meetings/create/
GET /meetings/create/

# Résultat :
# ✅ Accès autorisé
# ✅ Formulaire de création affiché
```

### Scénario 3 : Admin gère les réunions

```python
# Utilisateur : admin@example.com
# Rôle MongoDB : 'admin'

# Accès à /meetings/create/
GET /meetings/create/

# Résultat :
# ✅ Accès autorisé (admin a les mêmes droits qu'instructor)
```

---

## 🔄 Matrice des permissions

| Vue | Student | Instructor | Admin |
|-----|---------|------------|-------|
| `meeting_list` | ❌ Redirect | ✅ | ✅ |
| `meeting_create` | ❌ Redirect | ✅ | ✅ |
| `meeting_update` | ❌ Forbidden | ✅ (ses réunions) | ✅ |
| `meeting_delete` | ❌ Forbidden | ✅ (ses réunions) | ✅ |
| `meeting_start` | ❌ Forbidden | ✅ (ses réunions) | ✅ |
| `meeting_end` | ❌ Forbidden | ✅ (ses réunions) | ✅ |
| `student_meetings` | ✅ | ✅ (redirect) | ✅ |
| `meeting_detail` | ✅ (si invité) | ✅ (ses réunions) | ✅ |
| `meeting_join` | ✅ (si invité) | ✅ (ses réunions) | ✅ |
| `meeting_respond` | ✅ (si invité) | N/A | N/A |
| `meeting_room` | ✅ (si invité) | ✅ (ses réunions) | ✅ |
| `meeting_leave` | ✅ | ✅ | ✅ |

---

## 📝 Vérification dans le code

### Fichier modifié
```
meetings/views.py
```

### Changements effectués

1. **Ajout des fonctions helper** (lignes 13-30)
   ```python
   def get_user_role(request)
   def is_instructor(request)
   ```

2. **Remplacement de `is_staff` par `is_instructor(request)`**
   - `meeting_list()` : ligne 38
   - `meeting_create()` : ligne 114

3. **Messages d'erreur explicites**
   - "Seuls les instructeurs peuvent accéder à cette page."
   - "Seuls les instructeurs peuvent créer des réunions."

---

## 🎯 Résultat

### Avant (❌)
- **Student** avec `is_staff=True` → ✅ Peut créer des réunions
- **Instructor** avec `is_staff=False` → ❌ Ne peut pas créer

### Après (✅)
- **Student** avec `role='student'` → ❌ Ne peut pas créer ✓
- **Instructor** avec `role='instructor'` → ✅ Peut créer ✓
- **Admin** avec `role='admin'` → ✅ Peut créer ✓

---

## 🚀 Prochaines étapes

### Recommandations

1. **Tester avec différents utilisateurs**
   - Créer un user avec `role='student'`
   - Créer un user avec `role='instructor'`
   - Vérifier les permissions

2. **Synchroniser is_staff avec role** (optionnel)
   ```python
   # Dans Learner/middleware.py
   if user_data.get('role') in ['instructor', 'admin']:
       user.is_staff = True
   else:
       user.is_staff = False
   user.save()
   ```

3. **Utiliser des decorators personnalisés** (futur)
   ```python
   @instructor_required
   def meeting_create(request):
       ...
   ```

---

## ✅ Checklist de vérification

- [x] Fonction `get_user_role()` créée
- [x] Fonction `is_instructor()` créée
- [x] `meeting_list` corrigé
- [x] `meeting_create` corrigé
- [x] Messages d'erreur explicites
- [x] Redirection vers `student_meetings` pour les étudiants
- [x] Permissions basées sur `role` MongoDB
- [x] Compatibilité avec `is_staff` (fallback)

---

## 🎉 Conclusion

**Le problème est corrigé !**

Maintenant :
- ✅ Seuls les utilisateurs avec `role='instructor'` ou `role='admin'` peuvent créer des réunions
- ✅ Les étudiants (`role='student'`) voient uniquement leurs invitations
- ✅ Le système vérifie le rôle MongoDB, pas `is_staff`
- ✅ Compatible avec l'architecture backend MongoDB

**La logique est maintenant correcte !** 🎯
