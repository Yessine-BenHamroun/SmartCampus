# Quick Start Guide - Fixed Version

## Prerequisites
- Python 3.8+
- MongoDB running locally or accessible
- Virtual environment activated

## Step 1: Start the Backend Server on Port 8001

### Option A: Using PowerShell Script (Recommended)
```powershell
# From project root
.\run_backend_8001.ps1
```

### Option B: Manual Command
```bash
cd backend
python manage.py runserver 8001
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8001/
Quit the server with CTRL-BREAK.
```

## Step 2: Verify Backend is Running

Open browser and test:
```
http://localhost:8001/api/courses/
```

Should return a JSON response with courses list.

## Step 3: Test Enrollment Flow

### 1. Login to get access token
```bash
curl -X POST http://localhost:8001/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"password123"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

### 2. Enroll in a course
```bash
curl -X POST http://localhost:8001/api/courses/{courseId}/enroll/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"
```

Expected: 201 Created

### 3. Get course status (check quiz/assignment availability)
```bash
curl -X GET http://localhost:8001/api/courses/{courseId}/status/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"
```

Response shows:
- `lessons[i].completed`: true/false
- `lessons[i].can_take_quiz`: true/false
- `can_take_assignment`: true/false

### 4. Complete a lesson
```bash
curl -X POST http://localhost:8001/api/courses/lesson/{lessonId}/complete/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"time_spent_minutes": 30}'
```

### 5. Try to access quiz (before lesson completion)
```bash
curl -X GET http://localhost:8001/api/courses/lesson/{lessonId}/quiz/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"
```

Expected: 403 Forbidden (if lesson not completed)

### 6. Try to access quiz (after lesson completion)
After completing the lesson, same request should return 200 OK with quiz data.

### 7. Try to access assignment (before all lessons completion)
```bash
curl -X GET http://localhost:8001/api/courses/assignment/{assignmentId}/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"
```

Expected: 403 Forbidden (if not all lessons completed)

### 8. Try to access assignment (after all lessons completion)
After completing all lessons, same request should return 200 OK with assignment data.

## Step 4: Frontend Testing

### In Browser Console
```javascript
// Get access token from session
const token = '{{ request.session.access_token }}';
const courseId = 'your-course-id';

// Test course status
fetch(`http://localhost:8001/api/courses/${courseId}/status/`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => console.log('Course Status:', data));

// Test lesson completion
fetch(`http://localhost:8001/api/courses/lesson/lesson-id/complete/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ time_spent_minutes: 30 })
})
.then(r => r.json())
.then(data => console.log('Lesson Completed:', data));
```

## Troubleshooting

### Issue: ERR_CONNECTION_REFUSED
**Solution:** Backend is not running on port 8001
- Run: `.\run_backend_8001.ps1`
- Or: `cd backend && python manage.py runserver 8001`

### Issue: 401 Unauthorized
**Solution:** Access token is invalid or expired
- Login again to get new token
- Check token is included in Authorization header

### Issue: 403 Forbidden on Quiz/Assignment
**Solution:** This is expected behavior!
- Complete the lesson first for quiz access
- Complete all lessons for assignment access
- Check course status to see what's available

### Issue: MongoDB Connection Error
**Solution:** MongoDB is not running
- Start MongoDB: `mongod`
- Or check connection string in settings.py

### Issue: Module Not Found Errors
**Solution:** Virtual environment not activated
- Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install requirements: `pip install -r backend/requirements.txt`

## Key Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/api/courses/{courseId}/enroll/` | Enroll in course | Required |
| GET | `/api/courses/{courseId}/status/` | Get course status & availability | Required |
| POST | `/api/courses/lesson/{lessonId}/complete/` | Mark lesson complete | Required |
| GET | `/api/courses/lesson/{lessonId}/quiz/` | Get quiz (gated) | Required |
| POST | `/api/courses/quiz/{quizId}/submit/` | Submit quiz | Required |
| GET | `/api/courses/assignment/{assignmentId}/` | Get assignment (gated) | Required |
| POST | `/api/courses/assignment/{assignmentId}/submit/` | Submit assignment | Required |

## Success Indicators

✅ Backend starts without errors on port 8001
✅ Enrollment endpoint returns 201 Created
✅ Course status shows lesson completion data
✅ Quiz returns 403 before lesson completion
✅ Quiz returns 200 after lesson completion
✅ Assignment returns 403 before all lessons completion
✅ Assignment returns 200 after all lessons completion
✅ Lesson completion updates progress percentage

## Next: Frontend Updates

Update your templates to:
1. Call `/api/courses/{courseId}/status/` on page load
2. Show "Complete lesson to unlock quiz" if `can_take_quiz` is false
3. Show "Complete all lessons to unlock assignment" if `can_take_assignment` is false
4. Refresh status after lesson completion

See `FIXES_APPLIED_ENROLLMENT_GATING.md` for detailed implementation guide.
