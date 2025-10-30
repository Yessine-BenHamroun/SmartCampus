# Student Certification Features - Testing Guide

## ✅ Server Status
- **Backend API:** Running on http://127.0.0.1:8001/
- **Frontend:** Running on http://127.0.0.1:8000/
- **Database:** MongoDB (smartcampus_db)

## Testing Steps

### 1. Login as Student
1. Go to http://127.0.0.1:8000/login/
2. Use student credentials (not instructor)
3. Verify you're logged in

### 2. Access Certification Features from Navigation

**Test Navigation Links:**
- Click on **"My Learning"** dropdown in header
- You should see new menu items:
  - ✅ My Certifications (with award icon)
  - ✅ My Badges (with trophy icon)

**Test Profile Dropdown:**
- Click on your username in top right
- Dropdown should show:
  - ✅ My Certifications
  - ✅ My Badges

### 3. Browse and Enroll in Certification

**From Course Page:**
1. Go to **Courses** → Click on a course
2. Scroll down to **"Course Certifications"** section
3. Find a certification card

**Check Student Buttons Appear:**
- ✅ If enrolled in course: "Start Certification" button (blue, award icon)
- ✅ If NOT enrolled: Warning message "Enroll in the course to access certifications"
- ❌ Instructor buttons (View, Edit, Steps, Delete) should NOT appear for students

**Enroll in Certification:**
1. Click **"Start Certification"** button
2. Should show loading spinner
3. Alert: "Successfully enrolled in certification! Redirecting..."
4. Automatically redirected to `/certification/<id>/steps/`

### 4. View Certification Steps

**Certification Steps Page:** `/certification/<certification_id>/steps/`

**Left Sidebar Should Show:**
- ✅ Certification badge/icon
- ✅ Title and description
- ✅ Progress bar (0/X steps initially)
- ✅ Status badge (In Progress)
- ✅ Total steps count
- ✅ Passing score requirement
- ✅ Exam attempts counter

**Main Content Should Show:**
- ✅ List of all steps in order
- ✅ Each step shows:
  - Step number badge
  - Title and description
  - Type badge (video/pdf/text)
  - "Required" badge if applicable
  - Content (video player, PDF link, or text)
  - "Mark as Complete" button (blue)

### 5. Complete Steps

**Test Step Completion:**
1. Click **"Mark as Complete"** on first step
2. Page should reload
3. Completed step should show:
   - ✅ Green checkmark icon
   - ✅ "Completed" button (disabled, green)
4. Progress bar should update (1/X steps)
5. Sidebar progress should increase

**Complete All Steps:**
- Mark all steps as complete one by one
- Progress bar should reach 100%
- Final exam section should appear

### 6. Take Final Exam (Placeholder)

**When All Steps Complete:**
- ✅ "Final Exam" section appears (yellow/warning background)
- ✅ Message: "All steps completed! You can now take the final exam."
- ✅ "Take Final Exam" button available
- ✅ Shows passing score requirement
- ✅ Shows exam attempts (0/3)

**Click "Take Final Exam":**
- Modal should open
- Shows warning about attempts remaining
- Placeholder message (exam system to be integrated with quiz)

### 7. View All Certification Progress

**Navigate to My Certifications:**
1. Click **"My Learning"** → **"My Certifications"**
2. URL: `/my-certification-progress/`

**Page Should Show:**
- ✅ Grid of certification cards (one per enrolled certification)
- ✅ Each card shows:
  - Certification icon/badge
  - Title
  - Progress bar
  - Status badge (In Progress/Completed/Failed)
  - Exam attempts (X/3)
  - Started date
  - "Continue" button (blue) if in progress
  - "View Badge" button (green) if completed

**If No Certifications:**
- ✅ Empty state with message "No Certifications Yet"
- ✅ "Browse Courses" button

### 8. View Badges

**Navigate to My Badges:**
1. Click **"My Learning"** → **"My Badges"**
2. URL: `/my-badges/`

**Expected:**
- Badge display page (from existing implementation)
- Shows all earned badges
- Verification codes

## Test Checklist

### ✅ Access Control
- [ ] Student can see "Start Certification" button
- [ ] Student CANNOT see instructor buttons (View, Edit, Steps, Delete)
- [ ] Must be enrolled in course to start certification
- [ ] Cannot access certification steps without enrolling

### ✅ Enrollment
- [ ] "Start Certification" button works
- [ ] Shows loading spinner during enrollment
- [ ] Success alert appears
- [ ] Redirects to steps page automatically
- [ ] Prevents duplicate enrollment (if click again, shows "Already enrolled")

### ✅ Steps Display
- [ ] All steps load correctly
- [ ] Steps shown in order
- [ ] Video content displays
- [ ] PDF links work
- [ ] Text content renders properly
- [ ] Progress sidebar updates

### ✅ Progress Tracking
- [ ] Progress bar updates when steps completed
- [ ] Completed steps show checkmark
- [ ] "Mark as Complete" button becomes disabled after completion
- [ ] Progress persists (reload page, still completed)

### ✅ Navigation
- [ ] "My Certifications" link in dropdown works
- [ ] "My Badges" link in dropdown works
- [ ] Breadcrumbs show correct path
- [ ] Back navigation works

### ✅ Visual Design
- [ ] Student buttons styled correctly (blue primary color)
- [ ] Icons display properly (bi-award, bi-trophy, etc.)
- [ ] Progress bars animated/styled nicely
- [ ] Status badges color-coded (primary, success, danger)
- [ ] Responsive design (works on mobile/tablet)

## Known Limitations (Future Enhancements)

1. **Exam System:** Placeholder modal, needs integration with quiz system
2. **Badge Award:** Requires exam completion (not yet functional)
3. **Notifications:** No email/alerts for progress updates
4. **Certificates:** PDF generation not implemented
5. **Social Sharing:** Badge sharing not yet available

## Troubleshooting

### If "Start Certification" Button Not Showing:
- Verify you're logged in as a student (not instructor)
- Ensure you're enrolled in the course
- Check that certification is active (`is_active=True`)
- Check browser console for JavaScript errors

### If Steps Not Loading:
- Check backend server is running on port 8001
- Verify JWT token is valid (check browser console)
- Check MongoDB connection
- Look for errors in backend terminal

### If Progress Not Updating:
- Check network tab for API call success
- Verify backend `/api/certifications/steps/complete/` endpoint works
- Check MongoDB for `student_progress` collection
- Clear browser cache and reload

### If Pages Return 404:
- Verify all URLs are added to `Learner/urls.py`
- Check URL name matches in templates
- Restart Django server after URL changes

## Success Criteria

✅ **All features working if:**
1. Student can navigate to certifications from menu
2. Student can enroll by clicking button
3. Student redirected to steps page
4. Student can complete steps
5. Progress tracked and displayed correctly
6. "My Certifications" page shows all progress
7. No instructor buttons visible to students

---

**Test Date:** October 30, 2025
**Tested By:** _____________
**Status:** Ready for Testing
**Notes:** _____________________________________________
