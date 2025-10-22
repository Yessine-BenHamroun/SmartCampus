# 🚀 QUICK START GUIDE - SmartCampus Django Project

## ⚡ Fast Setup (5 Minutes)

### Option 1: Automated Setup (Recommended)

1. **Open PowerShell in the project directory**
2. **Run the setup script:**
   ```powershell
   .\setup.ps1
   ```
   
   If you get an error, first run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Configure MongoDB** (Choose one):
   
   **For Local MongoDB:**
   - Install from: https://www.mongodb.com/try/download/community
   - Start service: `net start MongoDB`
   
   **For MongoDB Atlas (Cloud - Free):**
   - Sign up: https://www.mongodb.com/cloud/atlas
   - Create cluster → Get connection string
   - Edit `.env` file and update `MONGO_URI`

4. **Run the server:**
   ```powershell
   python manage.py runserver
   ```
   
   Or simply double-click: `run.bat`

5. **Open browser:** http://localhost:8000

---

### Option 2: Manual Setup

```powershell
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
Copy-Item .env.example .env
# Edit .env with your settings

# 4. Update templates
python update_templates.py

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Run migrations
python manage.py migrate

# 7. Start server
python manage.py runserver
```

---

## 📝 What Was Created

Your Django project now has:

✅ **Project Structure**
- `smartcampus/` - Main Django project
- `learner/` - Your app with all HTML templates
- `static/` - CSS, JS, images from your Learner template
- `templates/` - Django-ized HTML templates

✅ **MongoDB Integration**
- Configured with djongo
- Ready for local MongoDB or Atlas

✅ **All Your Pages Working**
- Home (index)
- About
- Courses & Course Details
- Instructors & Instructor Profile
- Blog & Blog Details
- Contact, Events, Enrollment
- Pricing, Privacy, Terms

✅ **Deployment Ready**
- `render.yaml` for Render deployment
- `requirements.txt` with all dependencies
- WhiteNoise for static files
- Gunicorn for production server

---

## 🎯 Testing Your Template (First Step)

1. **Start the server:**
   ```powershell
   python manage.py runserver
   ```

2. **Test these URLs:**
   - Home: http://localhost:8000/
   - Courses: http://localhost:8000/courses/
   - Instructors: http://localhost:8000/instructors/
   - Blog: http://localhost:8000/blog/
   - Contact: http://localhost:8000/contact/
   - Admin: http://localhost:8000/admin/

3. **Check that:**
   - ✅ Pages load correctly
   - ✅ CSS styles are applied
   - ✅ Navigation works
   - ✅ Images appear
   - ✅ JavaScript works (dropdowns, animations)

---

## 🔍 Troubleshooting

### "Module not found" errors
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### MongoDB connection error
```powershell
# Check if MongoDB is running
net start MongoDB

# Or edit .env file with correct MONGO_URI
```

### Static files not loading
```powershell
python manage.py collectstatic --noinput
python manage.py runserver
```

### PowerShell execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📂 Important Files

- **`.env`** - Your configuration (MongoDB, SECRET_KEY)
- **`manage.py`** - Django management commands
- **`learner/views.py`** - View functions for each page
- **`learner/urls.py`** - URL routing
- **`learner/models.py`** - Database models (add yours here)
- **`smartcampus/settings.py`** - Django settings

---

## 🎓 Next Steps After Template Testing

Once your template is working, implement features:

### 1. **Add Dynamic Data**
Edit `learner/models.py` to create models:
```python
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    # ... more fields
```

### 2. **Update Views**
Edit `learner/views.py` to fetch data:
```python
def courses(request):
    courses = Course.objects.all()
    return render(request, 'learner/courses.html', {'courses': courses})
```

### 3. **Update Templates**
Use Django template variables in HTML:
```html
{% for course in courses %}
    <h3>{{ course.title }}</h3>
    <p>{{ course.description }}</p>
{% endfor %}
```

### 4. **Add Forms**
Create forms for enrollment, contact, etc.

### 5. **Add Authentication**
Implement user login/registration

---

## 🚀 Deploy to Render

1. Push code to GitHub
2. Connect to Render (https://render.com)
3. Set environment variables
4. Deploy!

See full deployment instructions in `README.md`

---

## 💡 Quick Commands Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run server
python manage.py runserver

# Run server (batch file)
.\run.bat

# Create admin user
python manage.py createsuperuser

# Make migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell
```

---

## ✅ Checklist

Before you continue development:

- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] MongoDB running (local or Atlas)
- [ ] .env file configured
- [ ] Templates updated with Django tags
- [ ] Static files collected
- [ ] Server running successfully
- [ ] Home page loads at http://localhost:8000
- [ ] Navigation works between pages
- [ ] Styles and scripts loading correctly

---

**You're all set! 🎉**

The template is now running as a Django project. You can start adding backend functionality, database models, and dynamic content.

For detailed information, see `README.md`
