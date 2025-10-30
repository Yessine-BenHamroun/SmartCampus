# 🎥 Meetings API Documentation

## Base URL
```
http://localhost:8001/api/meetings/
```

---

## 🔐 Authentication
All endpoints require JWT authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

---

## 📋 Endpoints

### 1. List Meetings / Create Meeting

#### **GET** `/api/meetings/`
Get all meetings:
- **Instructors**: Get all meetings they created
- **Students**: Get all meetings they are invited to

**Response:**
```json
{
  "success": true,
  "count": 2,
  "meetings": [
    {
      "id": "507f1f77bcf86cd799439011",
      "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Python Advanced Course",
      "description": "Advanced Python concepts",
      "instructor_id": "507f1f77bcf86cd799439012",
      "instructor_email": "prof@example.com",
      "scheduled_date": "2025-11-01T14:00:00",
      "duration": 60,
      "meeting_link": "https://meet.jit.si/SmartCampus-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "status": "scheduled",
      "started_at": null,
      "ended_at": null,
      "created_at": "2025-10-30T10:00:00",
      "updated_at": "2025-10-30T10:00:00"
    }
  ]
}
```

#### **POST** `/api/meetings/` (Instructors only)
Create a new meeting.

**Request Body:**
```json
{
  "title": "Python Advanced Course",
  "description": "Learn advanced Python topics",
  "scheduled_date": "2025-11-01T14:00:00",
  "duration": 60,
  "student_ids": [
    "507f1f77bcf86cd799439013",
    "507f1f77bcf86cd799439014"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meeting created successfully",
  "meeting": {
    "id": "507f1f77bcf86cd799439011",
    "meeting_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Python Advanced Course",
    "meeting_link": "https://meet.jit.si/SmartCampus-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    ...
  }
}
```

**Errors:**
- `403`: Not an instructor
- `400`: Missing required fields or invalid date

---

### 2. Meeting Details

#### **GET** `/api/meetings/<meeting_id>/`
Get meeting details with participants.

**Response:**
```json
{
  "success": true,
  "meeting": {
    "id": "507f1f77bcf86cd799439011",
    "title": "Python Advanced Course",
    ...
  },
  "participants": [
    {
      "id": "507f1f77bcf86cd799439015",
      "meeting_id": "507f1f77bcf86cd799439011",
      "student_id": "507f1f77bcf86cd799439013",
      "student_email": "student1@example.com",
      "status": "invited",
      "joined_at": null,
      "left_at": null,
      "created_at": "2025-10-30T10:00:00",
      "updated_at": "2025-10-30T10:00:00"
    }
  ],
  "is_instructor": true
}
```

**Errors:**
- `404`: Meeting not found
- `403`: Not invited to meeting (for students)

#### **PUT** `/api/meetings/<meeting_id>/` (Instructor only)
Update meeting details.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "duration": 90,
  "scheduled_date": "2025-11-01T15:00:00",
  "student_ids": ["507f1f77bcf86cd799439013"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meeting updated successfully",
  "meeting": { ... }
}
```

**Errors:**
- `403`: Not the instructor
- `400`: Meeting already started/ended

#### **DELETE** `/api/meetings/<meeting_id>/` (Instructor only)
Cancel meeting.

**Response:**
```json
{
  "success": true,
  "message": "Meeting cancelled successfully"
}
```

---

### 3. Start Meeting

#### **POST** `/api/meetings/<meeting_id>/start/` (Instructor only)
Start a scheduled meeting.

**Response:**
```json
{
  "success": true,
  "message": "Meeting started successfully",
  "meeting": {
    "id": "507f1f77bcf86cd799439011",
    "status": "ongoing",
    "started_at": "2025-11-01T14:00:00",
    ...
  }
}
```

**Errors:**
- `403`: Not the instructor
- `400`: Meeting not scheduled
- `404`: Meeting not found

---

### 4. End Meeting

#### **POST** `/api/meetings/<meeting_id>/end/` (Instructor only)
End an ongoing meeting.

**Response:**
```json
{
  "success": true,
  "message": "Meeting ended successfully",
  "meeting": {
    "id": "507f1f77bcf86cd799439011",
    "status": "completed",
    "ended_at": "2025-11-01T15:00:00",
    ...
  }
}
```

**Errors:**
- `403`: Not the instructor
- `400`: Meeting not ongoing

---

### 5. Join Meeting

#### **POST** `/api/meetings/<meeting_id>/join/`
Join an ongoing meeting (marks as attended).

**Response:**
```json
{
  "success": true,
  "message": "Joined meeting successfully",
  "meeting_link": "https://meet.jit.si/SmartCampus-a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Errors:**
- `403`: Not invited
- `400`: Meeting not active
- `404`: Meeting not found

---

### 6. Leave Meeting

#### **POST** `/api/meetings/<meeting_id>/leave/`
Leave meeting (records leave time).

**Response:**
```json
{
  "success": true,
  "message": "Left meeting successfully",
  "duration": 45
}
```

---

### 7. Respond to Invitation

#### **POST** `/api/meetings/<meeting_id>/respond/`
Accept or decline meeting invitation.

**Request Body:**
```json
{
  "action": "accept"  // or "decline"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meeting invitation accepted successfully"
}
```

**Errors:**
- `400`: Invalid action
- `403`: Not invited
- `404`: Meeting not found

---

### 8. Student Meetings

#### **GET** `/api/meetings/my/invitations/`
Get all meetings for current student.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "meetings": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Python Advanced Course",
      "participant_status": "accepted",
      "joined_at": null,
      "left_at": null,
      ...
    }
  ]
}
```

---

## 📊 Data Models

### Meeting
```json
{
  "id": "string (ObjectId)",
  "meeting_id": "string (UUID)",
  "title": "string",
  "description": "string",
  "instructor_id": "string (ObjectId)",
  "instructor_email": "string",
  "scheduled_date": "datetime (ISO 8601)",
  "duration": "number (minutes)",
  "meeting_link": "string (URL)",
  "status": "scheduled|ongoing|completed|cancelled",
  "started_at": "datetime|null",
  "ended_at": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### MeetingParticipant
```json
{
  "id": "string (ObjectId)",
  "meeting_id": "string (ObjectId)",
  "student_id": "string (ObjectId)",
  "student_email": "string",
  "status": "invited|accepted|declined|attended|absent",
  "joined_at": "datetime|null",
  "left_at": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## 🔄 Status Flow

### Meeting Status
```
scheduled → ongoing → completed
                 ↓
             cancelled
```

### Participant Status
```
invited → accepted/declined → attended → (with joined_at/left_at)
      ↓
   absent (if not attended)
```

---

## 🎯 Use Cases

### Instructor Creates Meeting
```bash
POST /api/meetings/
{
  "title": "Machine Learning Basics",
  "description": "Introduction to ML",
  "scheduled_date": "2025-11-02T10:00:00",
  "duration": 90,
  "student_ids": ["id1", "id2", "id3"]
}
```

### Student Accepts Invitation
```bash
POST /api/meetings/<meeting_id>/respond/
{
  "action": "accept"
}
```

### Instructor Starts Meeting
```bash
POST /api/meetings/<meeting_id>/start/
```

### Student Joins Meeting
```bash
POST /api/meetings/<meeting_id>/join/
# Response includes meeting_link to redirect to Jitsi
```

### Instructor Ends Meeting
```bash
POST /api/meetings/<meeting_id>/end/
```

---

## 🛡️ Permissions

| Action | Student | Instructor |
|--------|---------|------------|
| List meetings | ✅ (invitations) | ✅ (created) |
| Create meeting | ❌ | ✅ |
| View details | ✅ (if invited) | ✅ (own) |
| Update meeting | ❌ | ✅ (own) |
| Delete meeting | ❌ | ✅ (own) |
| Start meeting | ❌ | ✅ (own) |
| End meeting | ❌ | ✅ (own) |
| Join meeting | ✅ (if invited) | ✅ (own) |
| Respond | ✅ (if invited) | N/A |

---

## 💾 MongoDB Collections

### `meetings`
Stores meeting information.

### `meeting_participants`
Stores participant information and attendance.

### Indexes
- `meetings`: `instructor_id`, `scheduled_date`, `status`
- `meeting_participants`: `meeting_id`, `student_id`

---

## 🧪 Testing

### Create Test Instructor
```bash
POST /api/users/register/
{
  "email": "instructor@test.com",
  "username": "instructor1",
  "password": "password123",
  "role": "instructor"
}
```

### Create Test Students
```bash
POST /api/users/register/
{
  "email": "student1@test.com",
  "username": "student1",
  "password": "password123",
  "role": "student"
}
```

### Login & Get Token
```bash
POST /api/users/login/
{
  "email": "instructor@test.com",
  "password": "password123"
}
# Returns access_token
```

### Create Meeting (with token)
```bash
curl -X POST http://localhost:8001/api/meetings/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "scheduled_date": "2025-11-01T14:00:00",
    "duration": 60,
    "student_ids": ["<student_id>"]
  }'
```

---

## 📝 Notes

- All dates are in UTC ISO 8601 format
- Meeting links are automatically generated using UUID
- Only instructors with `role='instructor'` can create meetings
- Students can only see meetings they are invited to
- Meeting link format: `https://meet.jit.si/SmartCampus-{meeting_id}`
