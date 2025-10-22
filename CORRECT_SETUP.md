# 🚀 How to Run SmartCampus (CORRECTED)

## ✅ CORRECT WAY - Use Root Directory

### 1. Activate Virtual Environment
```powershell
cd C:\Users\yessi\Desktop\5TWIN\Django\SmartCampus
.\venv\Scripts\Activate.ps1
```

### 2. Run Frontend Server (Port 8000)
```powershell
python manage.py runserver 8000
```

### 3. Run Backend API Server (Port 8001) - In Another Terminal
```powershell
cd C:\Users\yessi\Desktop\5TWIN\Django\SmartCampus
.\venv\Scripts\Activate.ps1
cd backend
python manage.py runserver 8001
```

---

## 📁 Project Structure (CORRECTED)

```
C:\Users\yessi\Desktop\5TWIN\Django\SmartCampus\
│
├── venv/                          ✅ ROOT venv - USE THIS!
│
├── manage.py                      ✅ Frontend Django project (port 8000)
├── smartcampus/                   ✅ Settings & URLs
├── Learner/                       ✅ Main app with templates
│   ├── templates/learner/         👈 EDIT THESE templates
│   ├── static/                    👈 CSS, JS, images here
│   └── views.py
│
├── backend/                       ✅ REST API (port 8001)
│   ├── manage.py
│   ├── config/
│   ├── users/
│   ├── courses/
│   └── blog/
│
└── frontend/                      ❌ DELETE THIS - It's a duplicate!
    ├── venv/                      ❌ Old venv (was here by mistake)
    └── ...

```

---

## ⚠️ What Was Wrong Before

**WRONG:**
- Running server from `frontend/` folder
- Using `frontend/venv/`
- Editing templates in `frontend/Learner/templates/`

**CORRECT:**
- Run server from ROOT (`SmartCampus/`)
- Use ROOT `venv/`
- Edit templates in `Learner/templates/`

---

## 🗑️ Cleanup Steps

1. **Stop any servers running in the frontend folder**
2. **Delete the frontend folder:**
   ```powershell
   # Make sure you're in the root directory
   cd C:\Users\yessi\Desktop\5TWIN\Django\SmartCampus
   
   # Remove frontend folder (after stopping all processes)
   Remove-Item -Path "frontend" -Recurse -Force
   ```

---

## ✅ Quick Test

After cleanup, test that everything works:

```powershell
# 1. Activate root venv
.\venv\Scripts\Activate.ps1

# 2. Start frontend server
python manage.py runserver 8000

# 3. Visit http://127.0.0.1:8000/
```

You should see your SmartCampus website! 🎉

---

## 📝 Notes

- **Frontend Django:** `http://127.0.0.1:8000/` (templates, static files)
- **Backend API:** `http://127.0.0.1:8001/api/` (REST API endpoints)
- **Make changes in:** `Learner/templates/learner/*.html`
- **Static files in:** `Learner/static/`
