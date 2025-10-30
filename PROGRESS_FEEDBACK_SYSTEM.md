# Gestion de Progression et Feedback - SmartCampus

## Vue d'ensemble

Ce système permet aux étudiants de:
1. **Suivre leur progression** dans chaque cours
2. **Évaluer les cours** (rating + commentaires)
3. **Évaluer les tuteurs/instructeurs** (rating + commentaires détaillés)

Avec **contrôle de saisie** (validation) et **jointures** (relations entre entités).

---

## 1. Gestion de Progression (Progress Tracking)

### Modèle: `StudentProgress`

**Champs:**
- `student_id` - ID de l'étudiant
- `course_id` - ID du cours
- `enrollment_id` - ID de l'inscription (jointure)
- `lessons_completed` - Liste des leçons complétées
- `quizzes_completed` - Liste des quiz complétés avec scores
- `assignments_completed` - Liste des assignments complétés avec scores
- `completion_percentage` - Pourcentage de complétion (calculé automatiquement)
- `last_accessed` - Dernière visite
- `time_spent_minutes` - Temps passé total

### API Endpoints

#### 1. Voir la progression d'un cours
```http
GET /api/courses/{course_id}/progress/details/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "progress": {
    "_id": "...",
    "student_id": "...",
    "course_id": "...",
    "completion_percentage": 65.5,
    "lessons_completed": ["lesson1", "lesson2"],
    "quizzes_completed": [
      {
        "quiz_id": "quiz1",
        "score": 85,
        "passed": true,
        "completed_at": "2025-10-29T..."
      }
    ],
    "assignments_completed": [
      {
        "assignment_id": "assign1",
        "score": 90,
        "passed": true,
        "completed_at": "2025-10-29T..."
      }
    ]
  },
  "course_title": "Python Programming"
}
```

#### 2. Voir toute la progression de l'étudiant
```http
GET /api/courses/progress/my/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "progress": [
    {
      "course_id": "...",
      "course_title": "Python Programming",
      "course_thumbnail": "...",
      "completion_percentage": 65.5,
      "lessons_completed": 10,
      "quizzes_completed": 3,
      "assignments_completed": 2
    }
  ],
  "total_courses": 5
}
```

#### 3. Marquer une leçon comme complétée
```http
POST /api/courses/lesson/{lesson_id}/complete/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "Lesson marked as completed",
  "progress": {
    "completion_percentage": 70.0,
    ...
  }
}
```

---

## 2. Gestion Feedback - Cours (Course Reviews)

### Modèle: `CourseReview`

**Champs:**
- `student_id` - ID de l'étudiant (jointure avec User)
- `course_id` - ID du cours (jointure avec Course)
- `rating` - Note de 1 à 5 étoiles ⭐
- `review_text` - Commentaire (min 10 caractères)
- `would_recommend` - Recommandation (true/false)

### Contrôle de Saisie (Validation)

✅ **Rating:** Doit être entre 1 et 5  
✅ **Review text:** Minimum 10 caractères  
✅ **Enrollment:** L'étudiant doit être inscrit au cours  
✅ **Unique:** Un étudiant ne peut donner qu'un seul avis par cours (update si existe)

### API Endpoints

#### 1. Soumettre/Modifier un avis sur un cours
```http
POST /api/courses/{course_id}/review/submit/
Authorization: Bearer {token}
Content-Type: application/json

{
  "rating": 5,
  "review_text": "Excellent cours! J'ai beaucoup appris.",
  "would_recommend": true
}
```

**Validation:**
- ✅ Rating: 1-5 (obligatoire)
- ✅ Review text: min 10 caractères (optionnel)
- ✅ Étudiant doit être inscrit au cours

**Response:**
```json
{
  "message": "Review submitted successfully",
  "review": {
    "_id": "...",
    "student_id": "...",
    "course_id": "...",
    "rating": 5,
    "review_text": "Excellent cours! J'ai beaucoup appris.",
    "would_recommend": true,
    "created_at": "2025-10-29T..."
  }
}
```

#### 2. Voir tous les avis d'un cours
```http
GET /api/courses/{course_id}/review/list/
```

**Response:**
```json
{
  "reviews": [
    {
      "_id": "...",
      "student_name": "John Doe",
      "rating": 5,
      "review_text": "Excellent cours!",
      "would_recommend": true,
      "created_at": "2025-10-29T..."
    }
  ],
  "statistics": {
    "average_rating": 4.5,
    "total_reviews": 25
  }
}
```

---

## 3. Gestion Feedback - Tuteurs (Instructor Reviews)

### Modèle: `InstructorReview`

**Champs:**
- `student_id` - ID de l'étudiant (jointure avec User)
- `instructor_id` - ID du tuteur (jointure avec User)
- `course_id` - ID du cours (jointure avec Course)
- `rating` - Note globale de 1 à 5 étoiles ⭐
- `review_text` - Commentaire (min 10 caractères)
- **Ratings détaillés:**
  - `teaching_quality` - Qualité d'enseignement (1-5)
  - `communication` - Communication (1-5)
  - `course_content` - Contenu du cours (1-5)

### Contrôle de Saisie (Validation)

✅ **Rating global:** Doit être entre 1 et 5  
✅ **Ratings détaillés:** Chacun entre 1 et 5  
✅ **Review text:** Minimum 10 caractères  
✅ **Enrollment:** L'étudiant doit être inscrit au cours du tuteur  
✅ **Unique:** Un étudiant ne peut donner qu'un seul avis par tuteur par cours

### API Endpoints

#### 1. Soumettre/Modifier un avis sur un tuteur
```http
POST /api/courses/instructor/{instructor_id}/course/{course_id}/review/
Authorization: Bearer {token}
Content-Type: application/json

{
  "rating": 5,
  "review_text": "Excellent professeur! Très pédagogue.",
  "teaching_quality": 5,
  "communication": 4,
  "course_content": 5
}
```

**Validation:**
- ✅ Rating: 1-5 (obligatoire)
- ✅ Teaching quality: 1-5 (optionnel)
- ✅ Communication: 1-5 (optionnel)
- ✅ Course content: 1-5 (optionnel)
- ✅ Review text: min 10 caractères (optionnel)
- ✅ Étudiant doit être inscrit au cours
- ✅ Le tuteur doit enseigner ce cours

**Response:**
```json
{
  "message": "Instructor review submitted successfully",
  "review": {
    "_id": "...",
    "student_id": "...",
    "instructor_id": "...",
    "course_id": "...",
    "rating": 5,
    "review_text": "Excellent professeur!",
    "teaching_quality": 5,
    "communication": 4,
    "course_content": 5,
    "created_at": "2025-10-29T..."
  }
}
```

#### 2. Voir tous les avis d'un tuteur
```http
GET /api/courses/instructor/{instructor_id}/reviews/
```

**Response:**
```json
{
  "reviews": [
    {
      "_id": "...",
      "student_name": "John Doe",
      "course_title": "Python Programming",
      "rating": 5,
      "review_text": "Excellent professeur!",
      "teaching_quality": 5,
      "communication": 4,
      "course_content": 5,
      "created_at": "2025-10-29T..."
    }
  ],
  "statistics": {
    "average_rating": 4.7,
    "average_teaching_quality": 4.8,
    "average_communication": 4.5,
    "average_course_content": 4.9,
    "total_reviews": 15
  }
}
```

---

## 4. Jointures (Relations)

### Relations dans le système:

```
StudentProgress
├── student_id → User (Student)
├── course_id → Course
└── enrollment_id → Enrollment

CourseReview
├── student_id → User (Student)
└── course_id → Course

InstructorReview
├── student_id → User (Student)
├── instructor_id → User (Instructor)
└── course_id → Course
```

### Exemple de jointure automatique:

Quand vous récupérez les avis, le système fait automatiquement les jointures:

```python
# Backend fait automatiquement:
review = CourseReview.find_by_course(course_id)
student = User.find_by_id(review.student_id)  # Jointure
course = Course.find_by_id(review.course_id)   # Jointure

# Résultat enrichi:
{
  "review": {...},
  "student_name": "John Doe",  # De la jointure User
  "course_title": "Python"     # De la jointure Course
}
```

---

## 5. Contrôle de Saisie (Input Validation)

### Validations automatiques:

#### Pour Course Review:
```python
# Rating validation
if rating < 1 or rating > 5:
    raise ValidationError("Rating must be between 1 and 5 stars")

# Review text validation
if review_text and len(review_text.strip()) < 10:
    raise ValidationError("Review must be at least 10 characters long")

# Enrollment check
if not Enrollment.find_one(student_id, course_id):
    raise ValidationError("You must be enrolled in this course")
```

#### Pour Instructor Review:
```python
# All ratings validation
for rating_field in [rating, teaching_quality, communication, course_content]:
    if rating_field and (rating_field < 1 or rating_field > 5):
        raise ValidationError("Rating must be between 1 and 5")

# Course-Instructor validation
if course.instructor_id != instructor_id:
    raise ValidationError("This instructor does not teach this course")
```

---

## 6. Exemples d'utilisation Frontend

### Afficher la progression d'un étudiant

```javascript
// Récupérer la progression
async function getMyProgress() {
  const response = await fetch('http://localhost:8001/api/courses/progress/my/', {
    headers: {
      'Authorization': 'Bearer ' + token
    }
  });
  
  const data = await response.json();
  
  // Afficher pour chaque cours
  data.progress.forEach(course => {
    console.log(`${course.course_title}: ${course.completion_percentage}%`);
  });
}
```

### Soumettre un avis sur un cours

```javascript
// Formulaire d'avis
async function submitCourseReview(courseId, rating, reviewText) {
  const response = await fetch(`http://localhost:8001/api/courses/${courseId}/review/submit/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
      rating: rating,
      review_text: reviewText,
      would_recommend: rating >= 4
    })
  });
  
  if (response.ok) {
    alert('Avis soumis avec succès!');
  } else {
    const error = await response.json();
    alert('Erreur: ' + error.details);
  }
}
```

### Soumettre un avis sur un tuteur

```javascript
// Formulaire d'avis tuteur
async function submitInstructorReview(instructorId, courseId, data) {
  const response = await fetch(
    `http://localhost:8001/api/courses/instructor/${instructorId}/course/${courseId}/review/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({
        rating: data.rating,
        review_text: data.reviewText,
        teaching_quality: data.teachingQuality,
        communication: data.communication,
        course_content: data.courseContent
      })
    }
  );
  
  if (response.ok) {
    alert('Avis sur le tuteur soumis avec succès!');
  }
}
```

---

## 7. Fichiers créés

### Backend:
- ✅ `backend/courses/models_progress.py` - Modèles (StudentProgress, CourseReview, InstructorReview)
- ✅ `backend/courses/serializers_progress.py` - Serializers avec validation
- ✅ `backend/courses/views_progress.py` - API endpoints
- ✅ `backend/courses/urls.py` - Routes (mis à jour)

---

## 8. Base de données MongoDB

### Collections créées:

```javascript
// student_progress
{
  _id: ObjectId,
  student_id: ObjectId,  // → users
  course_id: ObjectId,   // → courses
  enrollment_id: ObjectId, // → enrollments
  lessons_completed: [ObjectId],
  quizzes_completed: [{quiz_id, score, passed, completed_at}],
  assignments_completed: [{assignment_id, score, passed, completed_at}],
  completion_percentage: Number,
  last_accessed: Date,
  time_spent_minutes: Number,
  created_at: Date,
  updated_at: Date
}

// course_reviews
{
  _id: ObjectId,
  student_id: ObjectId,  // → users
  course_id: ObjectId,   // → courses
  rating: Number (1-5),
  review_text: String,
  would_recommend: Boolean,
  created_at: Date,
  updated_at: Date
}

// instructor_reviews
{
  _id: ObjectId,
  student_id: ObjectId,     // → users
  instructor_id: ObjectId,  // → users
  course_id: ObjectId,      // → courses
  rating: Number (1-5),
  review_text: String,
  teaching_quality: Number (1-5),
  communication: Number (1-5),
  course_content: Number (1-5),
  created_at: Date,
  updated_at: Date
}
```

---

## 9. Résumé des fonctionnalités

### ✅ Gestion de Progression
- Suivi automatique de la progression
- Calcul du pourcentage de complétion
- Historique des quiz et assignments
- Temps passé sur chaque cours

### ✅ Gestion Feedback Cours
- Rating 1-5 étoiles
- Commentaires textuels
- Recommandation
- Statistiques moyennes
- Un seul avis par étudiant par cours

### ✅ Gestion Feedback Tuteurs
- Rating global 1-5 étoiles
- Ratings détaillés (enseignement, communication, contenu)
- Commentaires textuels
- Statistiques détaillées
- Un seul avis par étudiant par tuteur par cours

### ✅ Contrôle de Saisie
- Validation des ratings (1-5)
- Validation de la longueur des commentaires (min 10 caractères)
- Vérification de l'inscription
- Vérification de l'appartenance cours-tuteur
- Messages d'erreur clairs

### ✅ Jointures
- StudentProgress → User, Course, Enrollment
- CourseReview → User, Course
- InstructorReview → User (Student), User (Instructor), Course
- Enrichissement automatique des données

---

## 10. Prochaines étapes (Frontend)

Pour compléter le système, il faut créer les pages frontend:

1. **Page "Ma Progression"** - Afficher tous les cours avec progression
2. **Page "Détails Cours"** - Ajouter section avis et rating
3. **Formulaire "Évaluer le cours"** - Modal ou page dédiée
4. **Formulaire "Évaluer le tuteur"** - Modal ou page dédiée
5. **Page "Profil Tuteur"** - Afficher les avis et statistiques

Voulez-vous que je crée ces pages frontend maintenant? 🚀
