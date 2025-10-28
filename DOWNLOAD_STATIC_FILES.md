# Fix CSS Loading Issue - SmartCampus

## Problem

The static files (CSS, JavaScript, images) from the BootstrapMade Learner template are missing.

## Solution

### Option 1: Download the Template (Recommended)

1. **Download the Learner Template**

   - Go to: https://bootstrapmade.com/learner-bootstrap-course-template/
   - Click "Download" (free version)
   - Extract the ZIP file

2. **Copy Static Files**
   Copy these folders from the downloaded template to your project:

   ```
   From: Learner-template/assets/
   To: C:\Users\Lenovo\Desktop\SmartCampus\SmartCampus\static\
   ```

   You should have:

   - `static/css/`
   - `static/js/`
   - `static/img/`
   - `static/vendor/`

3. **Collect Static Files**

   ```powershell
   # Activate virtual environment
   .\venv\Scripts\activate

   # Collect static files
   python manage.py collectstatic --noinput

   # Restart server
   python manage.py runserver
   ```

### Option 2: Use CDN Links (Quick Fix)

I'll modify the templates to use CDN links instead of local files.

This is temporary but will get the site working immediately.

---

## After Fixing

1. Stop the server (Ctrl+C)
2. Apply one of the solutions above
3. Restart the server: `python manage.py runserver`
4. Refresh your browser

The CSS should now load properly!
