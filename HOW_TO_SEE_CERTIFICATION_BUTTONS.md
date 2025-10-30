# Quick Guide: How to See Student Certification Buttons

## Problem

You're seeing "Enroll in the course to access certifications" instead of the "Start Certification" button.

## Solution

### Step 1: Enroll in the Course

1. On the course detail page, look for the **blue "Enroll Now" button** in the top-right area
2. Click **"Enroll Now"**
3. Wait for the success message
4. The page will reload automatically

### Step 2: View Certification Buttons

After enrolling, you'll see one of these buttons on each certification card:

**For Active Certifications:**

- 🔵 **"Start Certification"** button (blue with award icon)
  - Click this to enroll in the certification
  - You'll be redirected to the certification steps page

**If You Already Started:**

- 🟢 **"Continue Certification"** button (with progress indicator)
  - Shows "Progress: X/Y steps"
  - Status badge (In Progress/Completed/Failed)

**If You Completed:**

- ✅ **"View Badge"** button (green)
  - Badge earned notification
  - Link to My Badges page

## What You Should See

### Before Enrolling in Course:

```
┌─────────────────────────────────────┐
│  cloud certification 1              │
│  0 steps | 70% passing score        │
│                                     │
│  ⚠️ Enroll in the course to access  │
│     certifications                  │
└─────────────────────────────────────┘
```

### After Enrolling in Course (Student View):

```
┌─────────────────────────────────────┐
│  cloud certification 1              │
│  0 steps | 70% passing score        │
│                                     │
│  [🏆 Start Certification]  ← BUTTON │
└─────────────────────────────────────┘
```

### Instructor View (Different Buttons):

```
┌─────────────────────────────────────┐
│  cloud certification 1              │
│  0 steps | 70% passing score        │
│                                     │
│  [👁️ View] [✏️ Edit] [📋 Steps] [🗑️ Delete]  │
└─────────────────────────────────────┘
```

## Troubleshooting

### "Enroll Now" button not working?

- Check browser console for errors (F12)
- Make sure you're logged in
- Verify both servers are running (frontend:8000, backend:8001)

### Still seeing warning after enrolling?

- **Refresh the page** (F5)
- Clear browser cache
- Check that enrollment was successful (check "My Courses")

### Seeing instructor buttons instead of student buttons?

- You're logged in as an instructor
- Log out and log in with a student account
- Students see "Start Certification"
- Instructors see "View, Edit, Steps, Delete"

## Testing Flow

1. ✅ **Login as student**
2. ✅ **Browse courses** → Click on a course
3. ✅ **Click "Enroll Now"** (top right blue button)
4. ✅ **Scroll to certifications section**
5. ✅ **Click "Start Certification"** button
6. ✅ **Redirected to certification steps page**
7. ✅ **Complete steps** → Mark as complete
8. ✅ **View progress** in "My Certifications"

## Quick Test Command

To verify you're enrolled in a course, check "My Courses" page:

- Go to: http://127.0.0.1:8000/my-learning/
- You should see the enrolled course listed
- If not, enroll first from the course page

---

**Current Status:** Template error fixed ✅
**Next Step:** Enroll in course to see student buttons
