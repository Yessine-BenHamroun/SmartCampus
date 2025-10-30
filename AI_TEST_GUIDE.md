# 🧪 Guide de Test Rapide - AI Sentiment Analysis

## ✅ Système Installé et Prêt

L'analyse de sentiment AI est maintenant complètement intégrée dans votre chat en temps réel !

---

## 🚀 Comment Tester

### 1. Ouvrir le Chat
```
http://127.0.0.1:8000/chat/
```

### 2. Entrer dans un Salon de Chat
- Cliquer sur un salon existant ou créer un nouveau salon
- Vous serez redirigé vers `http://127.0.0.1:8000/chat/<room-slug>/`

### 3. Observer l'Analyse Automatique
- **Les messages existants** : Des badges de sentiment apparaîtront automatiquement
  * Exemple : "Hello! 😊 POSITIVE 95%"
  * Les badges peuvent prendre 2-3 secondes pour apparaître (première analyse)

- **Nouveaux messages** : Tapez un message et envoyez-le
  * Message positif : "This is amazing!" → Badge 😊
  * Message négatif : "This is terrible" → Badge 😞
  * Message neutre : "The meeting is tomorrow" → Badge 😐

### 4. Ouvrir le Panneau AI
- **Bouton** : Cliquer sur le bouton flottant 🤖 en bas à droite de l'écran
- **Panneau** : Un panneau latéral s'ouvrira avec :
  * 📊 Statistiques en temps réel
  * 🎯 Bouton "Analyser la Conversation"
  * ⚙️ Toggle "Auto-analyse des nouveaux messages"

### 5. Voir les Statistiques
- **Stats automatiques** : Le panneau affiche :
  * Pourcentage de messages positifs (vert)
  * Pourcentage de messages neutres (gris)
  * Pourcentage de messages négatifs (rouge)
  * Nombre total de messages analysés

### 6. Analyser la Conversation Complète
- **Bouton** : Cliquer sur "Analyser la Conversation"
- **Résultat** : Une section "Insights" apparaîtra avec :
  * 😊/😞/😐 Mood global de la conversation
  * Barres de progression montrant la distribution
  * Recommandations basées sur l'analyse :
    * ✅ Success : Conversation très positive
    * ⚠️ Warning : Quelques tensions
    * 🚨 Alert : Ambiance très négative

---

## 📝 Exemples de Messages à Tester

### Messages Positifs (😊)
```
- "This is amazing!"
- "Great work everyone!"
- "I love this chat system!"
- "Excellent presentation!"
- "Thank you so much!"
```

### Messages Négatifs (😞)
```
- "This is terrible"
- "I hate this"
- "This doesn't work"
- "Very frustrating"
- "This is awful"
```

### Messages Neutres (😐)
```
- "The meeting is tomorrow"
- "I will check this later"
- "Let me know when you're ready"
- "Here is the document"
- "Please review this"
```

---

## 🎯 Points de Vérification

### ✅ Checklist Visuelle

1. **Badge de sentiment sur les messages**
   - [ ] Les emojis apparaissent (😊 😞 😐)
   - [ ] Le label est affiché (POSITIVE, NEGATIVE, NEUTRAL)
   - [ ] Le pourcentage de confiance est visible

2. **Bouton flottant AI**
   - [ ] Icône 🤖 visible en bas à droite
   - [ ] Bouton réagit au survol (scale 1.1)
   - [ ] Clic ouvre le panneau latéral

3. **Panneau AI**
   - [ ] S'ouvre avec animation slide-up
   - [ ] Affiche les statistiques en grille (3 colonnes)
   - [ ] Bouton "Analyser la Conversation" fonctionne
   - [ ] Toggle "Auto-analyse" fonctionne

4. **Analyse en temps réel**
   - [ ] Nouveaux messages sont analysés automatiquement
   - [ ] Badge apparaît dans les 2-3 secondes
   - [ ] Stats du panneau se mettent à jour

---

## 🐛 Si Quelque Chose Ne Marche Pas

### Les badges n'apparaissent pas
1. **Ouvrir la Console** (F12 → Console)
2. **Chercher des erreurs** :
   - Erreur 404 sur `ai_sentiment.js` ? → Vérifier le fichier static
   - Erreur 404 sur `ai_sentiment.css` ? → Vérifier le fichier static
   - Erreur "Failed to fetch" ? → Vérifier que l'API fonctionne

3. **Tester l'API manuellement** :
   ```bash
   # Dans un nouveau terminal
   curl http://127.0.0.1:8000/chat/api/ai/analyze-sentiment/ \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"message_id": "test", "text": "This is great!"}'
   ```

### Le modèle est lent
- **Normal** : La première analyse prend 5-10 secondes (chargement du modèle)
- **Après** : Chaque analyse prend ~200-500ms
- **Solution** : Attendre que le modèle soit chargé en mémoire

### Erreur "No module named transformers"
```bash
# Dans le terminal du projet
.\.venv\Scripts\python.exe -m pip install transformers torch
```

---

## 📊 Collections MongoDB à Vérifier

### Après quelques tests, vérifier MongoDB Compass :

1. **Collection `message_sentiments`**
   - Devrait contenir les analyses individuelles
   - Champs : message_id, sentiment, score, emoji, analyzed_at

2. **Collection `conversation_insights`**
   - Créée après "Analyser la Conversation"
   - Champs : room_slug, mood, sentiment_distribution, recommendations

---

## 🎉 Résultat Attendu

### Écran de Chat avec AI

```
┌─────────────────────────────────────────────────────────┐
│  [← Retour]           Room Name      [Utilisateur: X]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  👤 John: Hello everyone!                              │
│         😊 POSITIVE 98%                                │
│         [14:30]                                         │
│                                                         │
│                              This is terrible! 😞      │
│                              NEGATIVE 99%     [14:31]  │
│                                                         │
│  👤 Jane: Great work!                                  │
│         😊 POSITIVE 99%                                │
│         [14:32]                                         │
│                                                         │
│  [Tapez votre message...              ] [Envoyer]     │
└─────────────────────────────────────────────────────────┘

                                    ┌────────────────┐
                                    │ 🤖 Analyse AI  │ ← Bouton flottant
                                    └────────────────┘

Panneau AI (quand ouvert) :
┌──────────────────────────────────┐
│ 🤖 Analyse AI du Chat       [×]  │
├──────────────────────────────────┤
│ 📊 Statistiques du Salon        │
│                                  │
│ 😊 Positif    😐 Neutre    😞 Négatif │
│    67%          20%          13%    │
│  10 msgs      3 msgs       2 msgs  │
│                                  │
│ [📊 Analyser la Conversation]   │
│                                  │
│ 💡 Insights:                    │
│ Mood: 😊 POSITIVE               │
│ ▓▓▓▓▓▓▓░░░ 67% Positif         │
│ ▓░░░░░░░░░ 13% Négatif         │
│                                  │
│ ✅ L'ambiance est excellente!   │
│                                  │
│ ☑ Auto-analyse activée          │
└──────────────────────────────────┘
```

---

## 🎯 Prochaines Étapes

Une fois que tout fonctionne :

1. **Tester avec plusieurs utilisateurs** :
   - Ouvrir plusieurs navigateurs
   - Se connecter avec différents comptes
   - Voir l'analyse en temps réel sur tous les clients

2. **Tester différents types de messages** :
   - Messages longs vs courts
   - Avec emojis
   - En anglais (meilleure précision)
   - En français (moins précis mais fonctionne)

3. **Observer les recommandations** :
   - Salon positif → Message de succès
   - Salon avec tensions → Warning
   - Salon très négatif → Alert

4. **Intégrations futures** :
   - Ajouter des graphiques (Chart.js)
   - Export des analyses en PDF
   - Notifications si l'ambiance devient négative
   - Modération automatique basée sur le sentiment

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Consulter** : `AI_SENTIMENT_GUIDE.md` (guide complet)
2. **Tester** : `test_ai_sentiment.py` (test du modèle)
3. **Logs Django** : Regarder le terminal du serveur
4. **Console Browser** : F12 → Console pour erreurs JS

---

**🎉 Amusez-vous bien avec votre système de chat intelligent !**
