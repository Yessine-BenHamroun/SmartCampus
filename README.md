# SmartCampus - Django Learning Management System

A modern learning management system built with Django (backend) and Bootstrap (frontend), using MongoDB as the database. Deployable on Render.

## 🚀 Features

- Modern, responsive Bootstrap template
- MongoDB integration using djongo
- Multiple pages: Home, Courses, Instructors, Blog, Events, etc.
- Ready for deployment on Render
- Static files management with WhiteNoise

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11.x
- MongoDB (locally installed OR MongoDB Atlas account)
- pip (Python package manager)
- Git (optional, for version control)

## 🔧 Local Development Setup

### Step 1: Set Up Virtual Environment

Open PowerShell and navigate to your project directory:

```powershell
cd c:\Users\yessi\Desktop\5TWIN\Django\SmartCampus

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

1. Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

2. Edit the `.env` file with your settings:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_URI=mongodb://localhost:27017/smartcampus
MONGO_DB_NAME=smartcampus
```

**Generate a secret key:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Set Up MongoDB

**Option A: Local MongoDB**
1. Install MongoDB Community Edition from https://www.mongodb.com/try/download/community
2. Start MongoDB service:
```powershell
net start MongoDB
```

**Option B: MongoDB Atlas (Cloud)**
1. Create a free account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get your connection string
4. Update `MONGO_URI` in `.env`:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/smartcampus?retryWrites=true&w=majority
```

### Step 5: Run Migrations

```powershell
python manage.py migrate
```

### Step 6: Create a Superuser (Optional)

```powershell
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 7: Collect Static Files

```powershell
python manage.py collectstatic --noinput
```

### Step 8: Run the Development Server

```powershell
python manage.py runserver
```

The application will be available at: **http://localhost:8000/**

## 🌐 Access the Application

- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Courses**: http://localhost:8000/courses/
- **Instructors**: http://localhost:8000/instructors/
- **Blog**: http://localhost:8000/blog/
- **Contact**: http://localhost:8000/contact/

## 📁 Project Structure

```
SmartCampus/
├── smartcampus/           # Main project settings
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── learner/               # Main application
│   ├── templates/         # HTML templates
│   │   └── learner/       # App-specific templates
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   └── admin.py           # Admin configuration
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── img/
│   └── vendor/
├── staticfiles/           # Collected static files (generated)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Example environment file
├── render.yaml            # Render deployment config
├── Procfile               # Process file for deployment
└── README.md              # This file
```

## 🎨 Template Pages

The following pages are available:
- **index.html** - Home page
- **about.html** - About page
- **courses.html** - Courses listing
- **course-details.html** - Course details
- **instructors.html** - Instructors listing
- **instructor-profile.html** - Instructor profile
- **blog.html** - Blog listing
- **blog-details.html** - Blog post details
- **contact.html** - Contact form
- **events.html** - Events page
- **enroll.html** - Enrollment page
- **pricing.html** - Pricing plans
- **privacy.html** - Privacy policy
- **terms.html** - Terms and conditions
- **404.html** - Error page

## 🚢 Deployment to Render

### Prerequisites
1. Create a Render account at https://render.com
2. Set up MongoDB Atlas (free tier available)
3. Push your code to GitHub

### Steps

1. **Prepare MongoDB Atlas**:
   - Create a database user
   - Whitelist all IPs (0.0.0.0/0) for Render access
   - Get your connection string

2. **Create New Web Service on Render**:
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Or manually configure:
     - **Build Command**: `pip install -r requirements.txt; python manage.py collectstatic --noinput`
     - **Start Command**: `gunicorn smartcampus.wsgi:application`

3. **Set Environment Variables**:
   - `SECRET_KEY`: Generate a new secret key
   - `DEBUG`: Set to `False`
   - `MONGO_URI`: Your MongoDB Atlas connection string
   - `MONGO_DB_NAME`: `smartcampus`
   - `ALLOWED_HOSTS`: Your Render URL (e.g., `your-app.onrender.com`)

4. **Deploy**: Render will automatically deploy your application

## 🛠️ Common Issues & Solutions

### Issue: "No module named 'djongo'"
**Solution**: Make sure you've activated your virtual environment and installed requirements:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: MongoDB connection error
**Solution**: 
- Check if MongoDB service is running: `net start MongoDB`
- Verify your MONGO_URI in .env file
- For Atlas, check network access settings

### Issue: Static files not loading
**Solution**: 
```powershell
python manage.py collectstatic --noinput
```

### Issue: "Execution policy" error when activating venv
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🔄 Next Steps

Now that the template is working, you can:

1. **Update Models**: Modify `learner/models.py` to add your data models
2. **Create API Endpoints**: Add REST API views for dynamic content
3. **Add Authentication**: Implement user login/registration
4. **Connect Frontend to Backend**: Update templates to use dynamic data from MongoDB
5. **Add Forms**: Create forms for course enrollment, contact, etc.
6. **Customize Templates**: Modify HTML templates to match your requirements

## 📚 Useful Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run Django shell
python manage.py shell

# Deactivate virtual environment
deactivate
```

## 📄 License

This project uses the Learner Bootstrap template from BootstrapMade.

## 🤝 Contributing

Feel free to fork this project and submit pull requests.

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Happy Coding! 🎓**
