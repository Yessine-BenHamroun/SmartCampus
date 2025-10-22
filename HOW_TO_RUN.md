# 🎯 HOW TO RUN YOUR DJANGO PROJECT

## ⚡ FASTEST WAY (Recommended)

### Step 1: Install Python Packages
Open PowerShell in your project folder and run:

```powershell
cd c:\Users\yessi\Desktop\5TWIN\Django\SmartCampus
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**If you get an execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Set Up MongoDB

**Option A - Quick Local Setup (Easiest for testing):**
1. Download MongoDB: https://www.mongodb.com/try/download/community
2. Install with default settings
3. Start MongoDB:
```powershell
net start MongoDB
```

**Option B - MongoDB Atlas (Cloud, Free):**
1. Go to: https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create a free cluster (takes 3-5 minutes)
4. Click "Connect" → "Connect your application"
5. Copy the connection string
6. Open `.env` file and replace the MONGO_URI line:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/smartcampus?retryWrites=true&w=majority
```

### Step 3: Update Templates
```powershell
python update_templates.py
```

### Step 4: Prepare Django
```powershell
python manage.py collectstatic --noinput
python manage.py migrate
```

### Step 5: Run the Server!
```powershell
python manage.py runserver
```

**Or simply double-click:** `run.bat`

### Step 6: Open Your Browser
Go to: **http://localhost:8000**

---

## 🎉 SUCCESS!

If you see your homepage with styles and everything working, you're done with step 1!

### What You Should See:
✅ Homepage loads with full styling
✅ Navigation menu works
✅ All pages accessible (About, Courses, Blog, etc.)
✅ Images and icons display correctly
✅ Responsive design works

---

## 🔧 If Something Doesn't Work

### Problem: "No module named 'django'"
**Solution:**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: "Can't connect to MongoDB"
**Solution:**
- For local: `net start MongoDB`
- For Atlas: Check your `.env` file has correct MONGO_URI

### Problem: "Static files not loading"
**Solution:**
```powershell
python manage.py collectstatic --noinput
```

### Problem: PowerShell won't run scripts
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📱 Testing Your Template

Visit these URLs to make sure everything works:

- **Home**: http://localhost:8000/
- **About**: http://localhost:8000/about/
- **Courses**: http://localhost:8000/courses/
- **Course Details**: http://localhost:8000/course-details/
- **Instructors**: http://localhost:8000/instructors/
- **Instructor Profile**: http://localhost:8000/instructor-profile/
- **Blog**: http://localhost:8000/blog/
- **Blog Details**: http://localhost:8000/blog-details/
- **Contact**: http://localhost:8000/contact/
- **Events**: http://localhost:8000/events/
- **Enroll**: http://localhost:8000/enroll/
- **Pricing**: http://localhost:8000/pricing/
- **Privacy**: http://localhost:8000/privacy/
- **Terms**: http://localhost:8000/terms/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🚀 Next Steps (After Template is Working)

### 1. Create Admin User (Optional)
```powershell
python manage.py createsuperuser
```
Then access admin panel at: http://localhost:8000/admin/

### 2. Start Adding Features

Now you can:
- **Add database models** in `learner/models.py`
- **Create forms** for user input
- **Add authentication** for user login
- **Connect templates to database** to show dynamic content
- **Build API endpoints** for your frontend
- **Add file uploads** for course materials
- **Implement search** functionality
- **Add payment integration** for course enrollment

### 3. Example: Add a Dynamic Course

**In `learner/models.py`:**
```python
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.title
```

**Run migrations:**
```powershell
python manage.py makemigrations
python manage.py migrate
```

**In `learner/views.py`:**
```python
def courses(request):
    courses = Course.objects.all()
    return render(request, 'learner/courses.html', {'courses': courses})
```

**In `learner/templates/learner/courses.html`:**
```html
{% for course in courses %}
    <div class="course-item">
        <h3>{{ course.title }}</h3>
        <p>{{ course.description }}</p>
        <span>${{ course.price }}</span>
    </div>
{% endfor %}
```

---

## 📚 Useful Commands

```powershell
# Activate virtual environment (always do this first)
.\venv\Scripts\Activate.ps1

# Run development server
python manage.py runserver

# Stop server
Press Ctrl+C in the terminal

# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Open Django shell (for testing)
python manage.py shell

# Check for errors
python manage.py check

# Deactivate virtual environment
deactivate
```

---

## 🌐 Deploy to Render (Later)

When ready to deploy:

1. **Create GitHub repository** and push your code
2. **Sign up at Render.com** (free tier available)
3. **Connect your GitHub repo**
4. **Set environment variables** in Render dashboard
5. **Deploy!**

Full deployment guide in `README.md`

---

## 📁 Project Structure Explained

```
SmartCampus/
├── manage.py              # Django command-line tool
├── .env                   # Your config (MongoDB, keys)
├── requirements.txt       # Python packages needed
├── run.bat               # Quick start script
├── update_templates.py   # Template converter script
│
├── smartcampus/          # Main project folder
│   ├── settings.py       # Django configuration
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # Server config
│
├── learner/              # Your main app
│   ├── models.py         # Database models (add yours here)
│   ├── views.py          # View functions (handles requests)
│   ├── urls.py           # URL patterns for this app
│   ├── admin.py          # Admin panel config
│   └── templates/        # Your HTML files
│       └── learner/      # HTML templates with Django tags
│
└── static/               # CSS, JS, images
    ├── css/              # Stylesheets
    ├── js/               # JavaScript files
    ├── img/              # Images
    └── vendor/           # Third-party libraries
```

---

## ✅ Checklist Before Moving Forward

- [ ] Python 3.11 installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] MongoDB running (local or Atlas)
- [ ] .env file configured
- [ ] Templates updated
- [ ] Static files collected
- [ ] Migrations run
- [ ] Server starts without errors
- [ ] Homepage loads at http://localhost:8000
- [ ] All pages accessible
- [ ] Styles and images loading correctly
- [ ] Navigation menu works

---

## 💡 Pro Tips

1. **Always activate virtual environment first**: `.\venv\Scripts\Activate.ps1`
2. **Keep server running while developing**: It auto-reloads on code changes
3. **Use Django admin panel**: Great for managing data
4. **Check terminal for errors**: They're usually very helpful
5. **Make small changes and test**: Don't change too much at once

---

## 🆘 Need Help?

1. Check `README.md` for detailed documentation
2. Read `QUICK_START.md` for quick reference
3. Check Django docs: https://docs.djangoproject.com
4. Check djongo docs: https://djongo.readthedocs.io/

---

**You're ready to start developing! 🎓🚀**

Your Learner template is now a fully functional Django project with MongoDB backend. Start adding features and building your SmartCampus platform!
