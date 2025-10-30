# Guide : Suppression de Messages avec Traçabilité

## 📋 Vue d'ensemble

La fonctionnalité de suppression de messages permet aux utilisateurs de supprimer leurs propres messages avec traçabilité complète. Le message supprimé reste visible avec l'indication "username a supprimé ce message".

## ✨ Fonctionnalités

### 1. **Suppression avec Traçabilité**
- ❌ **Soft Delete** : Les messages ne sont pas supprimés de la base de données
- 👤 **Identification** : Affiche qui a supprimé le message
- ⏰ **Horodatage** : L'heure du message original est conservée
- 🔒 **Sécurité** : Seul l'expéditeur peut supprimer son propre message

### 2. **Affichage Visuel**
- 🗑️ **Icône** : Icône de corbeille pour les messages supprimés
- 🎨 **Style** : Opacité réduite et couleur grise pour distinction
- 📝 **Texte** : "Prénom Nom a supprimé ce message" en italique

### 3. **Temps Réel**
- ⚡ **WebSocket** : Mise à jour instantanée pour tous les participants
- 🔄 **Synchronisation** : Tous les utilisateurs voient la suppression en temps réel

## 🎯 Comment tester

### Étape 1 : Accéder au Chat
```
1. Connectez-vous à SmartCampus
2. Allez sur http://127.0.0.1:8000/chat/
3. Cliquez sur un salon de chat
```

### Étape 2 : Envoyer un Message
```
1. Tapez un message dans le champ de saisie
2. Appuyez sur Entrée ou cliquez sur Envoyer
3. Votre message apparaît à droite avec une icône de corbeille 🗑️
```

### Étape 3 : Supprimer le Message
```
1. Survolez votre message
2. Cliquez sur l'icône de corbeille 🗑️ à côté de votre nom
3. Confirmez la suppression dans la boîte de dialogue
4. Le message devient : "🗑️ Votre Nom a supprimé ce message"
```

### Étape 4 : Vérifier la Synchronisation (optionnel)
```
1. Ouvrez le même salon dans un autre navigateur/onglet
2. Supprimez un message dans une fenêtre
3. Vérifiez que l'autre fenêtre voit la suppression instantanément
```

## 🔍 Vérifications Techniques

### 1. Base de Données
```sql
-- Le message est marqué comme supprimé, pas détruit
SELECT id, content, is_deleted, deleted_at FROM chat_chatmessage WHERE id = [message_id];
```

**Résultat attendu :**
```
id | content              | is_deleted | deleted_at
1  | [Message supprimé]   | True       | 2025-10-30 01:10:23
```

### 2. WebSocket Console
Ouvrez la console du navigateur (F12) et vérifiez les logs :

**Lors de la suppression :**
```javascript
🗑️ Suppression du message: 123
📨 Message reçu: {type: "message_deleted", message_id: 123, deleted_text: "Taher Ben Ismail a supprimé ce message"}
🗑️ Message supprimé: 123
```

### 3. Permissions
```
✅ Vous pouvez supprimer VOS messages → Bouton visible
❌ Vous NE pouvez PAS supprimer les messages des autres → Pas de bouton
```

## 🎨 Interface Utilisateur

### Messages Normaux
```html
┌─────────────────────────────────────────┐
│ Taher Ben Ismail              🗑️        │
│ Bonjour tout le monde !                 │
│                                    14:30 │
└─────────────────────────────────────────┘
```

### Messages Supprimés (Vos Messages)
```html
┌─────────────────────────────────────────┐
│ 🗑️ Taher Ben Ismail a supprimé ce msg  │
│                                    14:30 │
└─────────────────────────────────────────┘
Style : Fond gris, opacité 60%, texte italique
```

### Messages Supprimés (Autres)
```html
┌─────────────────────────────────────────┐
│ 🗑️ John Doe a supprimé ce message       │
│                                    14:25 │
└─────────────────────────────────────────┘
Style : Fond gris clair, texte gris, italique
```

## 🔧 Fichiers Modifiés

### 1. **Backend**
- ✅ `chat/models.py` : Ajout du champ `deleted_at`
- ✅ `chat/views.py` : Vue `delete_message` pour l'API
- ✅ `chat/urls.py` : Route `/message/<id>/delete/`
- ✅ `chat/consumers.py` : Gestion WebSocket de la suppression

### 2. **Frontend**
- ✅ `chat/templates/chat/chat_room.html` : Bouton suppression + affichage
- ✅ `chat/static/chat/js/chat.js` : Fonctions `deleteMessage()` et `handleMessageDeleted()`

### 3. **Base de Données**
- ✅ Migration : `chat/migrations/0002_chatmessage_deleted_at.py`

## 📊 Flux de Données

### Suppression via WebSocket (Temps Réel)
```
User clique sur 🗑️
    ↓
JavaScript : deleteMessage(id)
    ↓
WebSocket : {type: "delete_message", message_id: 123}
    ↓
Consumer : delete_message() → soft_delete()
    ↓
Broadcast : {type: "message_deleted", ...}
    ↓
Tous les clients : handleMessageDeleted()
    ↓
DOM mis à jour avec texte supprimé
```

### Suppression via API HTTP (Alternative)
```
User clique sur 🗑️
    ↓
JavaScript : fetch('/chat/message/123/delete/', {method: 'POST'})
    ↓
View : delete_message() → soft_delete()
    ↓
Response : {success: true, deleted_text: "..."}
    ↓
JavaScript met à jour le DOM
```

## 🛡️ Sécurité

### 1. **Vérification du Propriétaire**
```python
# Dans consumers.py
message = ChatMessage.objects.get(id=message_id, sender=self.user)
# ↑ Échoue si l'utilisateur n'est pas l'expéditeur
```

### 2. **Authentification**
```python
# Dans views.py
@login_required
@require_POST
def delete_message(request, message_id):
    if message.sender != request.user:
        return JsonResponse({'error': '...'}, status=403)
```

### 3. **Soft Delete**
```python
# Le contenu original est écrasé
self.content = "[Message supprimé]"
# Impossible de récupérer le contenu original
```

## 🐛 Dépannage

### Problème : Bouton de suppression non visible
**Solution :** Vérifiez que Bootstrap Icons est chargé
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```

### Problème : Suppression ne fonctionne pas
**Solution :** Vérifiez la console du navigateur (F12)
```javascript
// Doit afficher :
✅ WebSocket connecté avec succès
🗑️ Suppression du message: [id]
```

### Problème : Autres utilisateurs ne voient pas la suppression
**Solution :** Vérifiez que le WebSocket est actif
```bash
# Dans le terminal du serveur Django, vous devriez voir :
✅ user1 connected to room general
✅ user2 connected to room general
```

## 📝 Notes Importantes

1. **Traçabilité** : Les messages supprimés restent dans la base de données avec `is_deleted=True`
2. **Anonymat** : Le nom complet de l'utilisateur est affiché (pas le username)
3. **Irréversible** : Une fois supprimé, le contenu original ne peut pas être restauré
4. **Temps Réel** : La suppression se propage instantanément via WebSocket

## 🎓 Cas d'Usage

### Scénario 1 : Correction d'Erreur
```
User : Envoie "Rendez-vous à 14h00" (erreur)
User : Supprime le message
User : Envoie "Rendez-vous à 15h00" (correct)
Résultat : Le message erroné affiche "User a supprimé ce message"
```

### Scénario 2 : Information Sensible
```
User : Partage accidentellement un mot de passe
User : Supprime immédiatement le message
Résultat : Tous les participants voient "User a supprimé ce message"
```

### Scénario 3 : Modération
```
Instructor : Voit un message inapproprié d'un étudiant
Note : Actuellement, seul l'auteur peut supprimer
Future : Ajouter rôle modérateur pour suppression par admins
```

## 🚀 Améliorations Futures

1. **Suppression par Modérateurs** : Permettre aux admins/instructeurs de supprimer n'importe quel message
2. **Historique** : Garder un journal d'audit des suppressions
3. **Délai de Suppression** : Empêcher la suppression après X minutes
4. **Suppression en Masse** : Sélectionner plusieurs messages à supprimer
5. **Raison de Suppression** : Demander pourquoi le message est supprimé

## ✅ Checklist de Test

- [ ] Je peux voir le bouton 🗑️ sur mes messages
- [ ] Je NE vois PAS le bouton sur les messages des autres
- [ ] Le message devient gris avec texte "X a supprimé ce message"
- [ ] L'heure du message original est conservée
- [ ] Les autres utilisateurs voient la suppression en temps réel
- [ ] La confirmation de suppression s'affiche
- [ ] Le message reste dans la base de données (is_deleted=True)
- [ ] Les nouveaux utilisateurs qui rejoignent le salon ne voient pas le contenu supprimé

---

**Fonctionnalité implémentée avec succès ! ✨**
