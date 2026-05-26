# 🚀 PG Finder - Complete Step-by-Step Setup Guide

## 📋 Table of Contents
1. [Initial Setup](#initial-setup)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Installation Steps](#installation-steps)
5. [Configuration & Keys](#configuration--keys)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Initial Setup

### **Step 1: Clone/Verify Project Structure**

Your project should look like this:
```
d:\Pg_finder\
├── PgFinder/          # Main project folder
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── pgs/               # PG listings app
├── users/             # User management app
├── chat/              # Chat system app
├── templates/         # HTML templates
├── static/            # CSS, JS, images
├── manage.py
├── requirement.txt    # Python dependencies
├── db.sqlite3         # SQLite database (dev)
└── .env               # Environment variables
```

**If any folders are missing, let me know!**

---

## 🔌 Environment Configuration

### **Step 2: Create `.env` File**

1. In `d:\Pg_finder\`, create a new file called `.env`
2. Copy this template and fill in your keys:

```env
# ============================================
# CRITICAL: Fill ALL these fields
# ============================================

# 📧 EMAIL CONFIGURATION (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@pgfinder.com

# 🗺️ GOOGLE MAPS API KEY
GOOGLE_MAPS_EMBED_API_KEY=your-google-maps-api-key

# 💳 RAZORPAY PAYMENT KEYS (Test Mode)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-test-secret-key

# 🔑 DJANGO SECRET
SECRET_KEY=your-secret-key-here

# 🛡️ SECURITY
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 📊 DATABASE (Optional - only for PostgreSQL)
# DB_NAME=pgfinder_db
# DB_USER=pgfinder_user
# DB_PASSWORD=strong_password
# DB_HOST=localhost
# DB_PORT=5432
```

### **How to Get Each Key:**

#### **1️⃣ Google Maps API Key**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Maps Embed API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy and paste the key to `.env`

#### **2️⃣ Razorpay Test Keys**
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Sign up (if needed)
3. Navigate to **Settings** → **API Keys**
4. Copy **Key ID** and **Key Secret**
5. Paste them in `.env` (Test mode starts with `rzp_test_`)

#### **3️⃣ Gmail App Password**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Enable **2-Factor Authentication** (if not enabled)
3. Navigate to **App passwords**
4. Select **Mail** and **Windows Computer**
5. Google will generate a 16-character password
6. Use this as `EMAIL_HOST_PASSWORD` in `.env`

#### **4️⃣ Django Secret Key**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and paste in `.env`

---

## 📊 Database Setup

### **Step 3: Initialize SQLite Database**

The database is already set up with migrations, but let's verify:

```bash
# Navigate to project directory
cd d:\Pg_finder

# Apply all migrations
python manage.py migrate

# Create admin user (superuser)
python manage.py createsuperuser

# Expected output:
# Username: admin
# Email: admin@example.com
# Password: (enter your password)
# Password (again): (confirm password)
# Superuser created successfully.
```

---

## 📦 Installation Steps

### **Step 4: Install Python Dependencies**

```bash
# Make sure you're in the project directory
cd d:\Pg_finder

# If using virtual environment (RECOMMENDED)
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirement.txt

# Verify installation
pip list
```

**If `pip install` fails**, try:
```bash
pip install --upgrade pip
pip install -r requirement.txt --force-reinstall
```

### **Step 5: Verify Django Installation**

```bash
# Check Django version
python -m django --version

# Should output: 5.2.6 or similar

# Check for any issues
python manage.py check

# Expected output: System check identified 0 issues
```

---

## ⚙️ Configuration & Keys

### **Step 6: Verify Settings Configuration**

Edit `PgFinder/settings.py` and ensure these are present:

```python
# Should exist in your settings.py:
from decouple import config

# Email settings
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Google Maps
GOOGLE_MAPS_EMBED_API_KEY = config('GOOGLE_MAPS_EMBED_API_KEY')

# Razorpay
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET')

# Django Channels (for chat system)
ASGI_APPLICATION = 'PgFinder.asgi.application'
INSTALLED_APPS = [
    'daphne',  # Must be FIRST
    'channels',
    # ... rest of apps
]
```

### **Step 7: Create Superuser (If Not Done)**

```bash
python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: your-email@example.com
# Password: create-a-strong-password
# Password (again): confirm-password

# Optional: Create another user for testing
python manage.py createsuperuser
# Username: testuser
# Email: test@test.com
# Password: testpass123
```

---

## 🚀 Running the Application

### **Option A: Run with Simple Django Server (Development)**

```bash
# Navigate to project
cd d:\Pg_finder

# Activate virtual environment
venv\Scripts\activate

# Run server
python manage.py runserver

# Output should show:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

Visit: `http://localhost:8000`

### **Option B: Run with Daphne (WebSocket Support - Chat System)**

```bash
cd d:\Pg_finder
venv\Scripts\activate

# Run with Daphne (supports WebSocket for chat)
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application

# Output should show:
# 2024-XX-XX XX:XX:XX daphne (signal handling) exited, code=0, reason='shutdown by parent'
# 2024-XX-XX XX:XX:XX Started server process 1234
# 2024-XX-XX XX:XX:XX Uvicorn running on http://0.0.0.0:8000
```

**For development without Redis:**
- Edit `PgFinder/settings.py`
- Uncomment: `'BACKEND': 'channels.layers.InMemoryChannelLayer'`
- Comment out the Redis backend

---

## 🧪 Testing

### **Step 8: Test User Authentication**

1. **Go to**: `http://localhost:8000/user/register/`
2. **Create Test Account**:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `TestPass123!`
   - Select: "I am a Seeker" (for booking)

3. **Login**: `http://localhost:8000/user/login/`
   - Username: `testuser`
   - Password: `TestPass123!`

### **Step 9: Test Admin Panel**

1. **Go to**: `http://localhost:8000/admin/`
2. **Login with superuser**:
   - Username: `admin`
   - Password: (superuser password you created)
3. **You should see**:
   - Users
   - PG Listings
   - Bookings
   - Payments
   - Ratings & Reviews
   - Chat conversations
   - Notifications

### **Step 10: Test PG Listing Creation**

1. **Create Owner Account**:
   - Go to register
   - Check "I am an Owner"
   - Submit

2. **Create a PG**:
   - Login as owner
   - Go to `/pgs/pgregister/`
   - Fill details:
     - Title: "My Amazing PG"
     - Address: "123 Main St"
     - City: "Delhi"
     - State: "Delhi"
     - Price: "5000"
     - Sharing Type: "2-Sharing"
     - Furnishing: "Semi-Furnished"
   - Upload images
   - Submit

3. **View PG**:
   - Go to `/pgs/`
   - You should see your PG listed

### **Step 11: Test Payment System**

1. **Create Booking**:
   - Login as seeker
   - Find a PG
   - Click "Book Now"
   - Set check-in date
   - Submit booking

2. **Initiate Payment**:
   - Go to booking confirmation
   - Click "Proceed to Payment"
   - You should see Razorpay checkout popup

3. **Complete Test Payment**:
   - Use test card: `4111 1111 1111 1111`
   - Expiry: Any future date
   - CVV: Any 3 digits
   - Click Pay

4. **Verify**:
   - Check booking status → should be "Confirmed"
   - Check admin panel → Payment record created
   - Check notifications → Payment confirmation sent

### **Step 12: Test Search & Map**

1. **Go to**: `/pgs/advanced-search/`
2. **Test Filters**:
   - Enter search query (city name)
   - Set price range
   - Apply filters
3. **Check Results**: Should show filtered listings
4. **Map View**: Click "Map" button to see Google Maps integration

### **Step 13: Test Chat System** (Optional)

1. **Create 2 Test Accounts**
2. **Go to**: `/chat/` from any account
3. **Click**: "Start Chat" with another user
4. **Send Message**: Type and send
5. **Verify**: Message appears in real-time

---

## 🐛 Troubleshooting

### **Issue 1: "ModuleNotFoundError: No module named 'django'"**

**Solution**:
```bash
# Install dependencies
pip install -r requirement.txt

# Verify installation
python -c "import django; print(django.__version__)"
```

---

### **Issue 2: "ValueError: FileInput doesn't support uploading multiple files"**

**Solution**: Already fixed in your code, but verify in `pgs/forms.py`:
```python
# CORRECT:
widgets = {
    'pg_image': forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    })
}

# WRONG (don't use 'multiple': True):
# 'multiple': True  # ❌ Remove this
```

---

### **Issue 3: "No module named 'decouple'"**

**Solution**:
```bash
pip install python-decouple

# Verify
python -c "from decouple import config; print('OK')"
```

---

### **Issue 4: ".env file not found or not being read"**

**Solution**:
1. Verify `.env` is in `d:\Pg_finder\` (same level as `manage.py`)
2. Verify `.env` is NOT in `.gitignore`
3. Restart Django server
4. Test with:
   ```bash
   python manage.py shell
   from decouple import config
   print(config('RAZORPAY_KEY_ID'))
   # Should print your key, not empty
   ```

---

### **Issue 5: "Razorpay Key ID not configured"**

**Solution**:
```bash
# Verify .env is loaded
python manage.py shell

# Inside shell:
from django.conf import settings
print(settings.RAZORPAY_KEY_ID)
print(settings.RAZORPAY_KEY_SECRET)

# If empty, check:
# 1. .env file exists
# 2. Keys are correctly set in .env
# 3. Restart server after editing .env
```

---

### **Issue 6: "Django check failed with errors"**

**Solution**:
```bash
python manage.py check --deploy

# Check for specific errors
python manage.py check

# If errors persist, ensure:
# 1. All apps in INSTALLED_APPS exist
# 2. Database is migrated: python manage.py migrate
# 3. All settings are valid
```

---

### **Issue 7: "Database error / migrations not applied"**

**Solution**:
```bash
# Check migration status
python manage.py showmigrations

# Apply all migrations
python manage.py migrate

# If issues persist, reset database:
# WARNING: This deletes all data!
# rm db.sqlite3
# python manage.py migrate
# python manage.py createsuperuser
```

---

### **Issue 8: "Static files not loading (CSS/JS)"**

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify settings.py has:
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

---

### **Issue 9: "Redis connection refused" (Chat system)**

**Solution**:

If you're getting Redis errors with chat:

Option A: Use InMemoryChannelLayer (no Redis needed for dev):
```python
# In settings.py, use this instead of Redis config:
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

Option B: Install and run Redis:
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use Windows Subsystem for Linux (WSL):
# wsl --install ubuntu
# Then: sudo apt-get install redis-server
# Start: redis-server
```

---

### **Issue 10: "KeyboardInterrupt / Server won't start"**

**Solution**:
```bash
# Kill any existing process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Try different port
python manage.py runserver 0.0.0.0:8001

# Or restart with Daphne
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application
```

---

## 📱 Quick Test Checklist

After setup, verify everything works:

- [ ] Django server starts: `python manage.py runserver`
- [ ] Admin panel accessible: `http://localhost:8000/admin/`
- [ ] Superuser can login
- [ ] User registration works
- [ ] PG listing creation works
- [ ] Search filters work
- [ ] Payment system shows Razorpay popup
- [ ] Chat system works (if testing)
- [ ] Google Maps loads (if API key configured)

---

## 🎯 Common Commands Reference

```bash
# Start server
python manage.py runserver

# Start with Daphne (chat support)
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application

# Create superuser
python manage.py createsuperuser

# Apply migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Check for errors
python manage.py check

# Install dependencies
pip install -r requirement.txt

# Upgrade pip
pip install --upgrade pip

# Freeze current dependencies
pip freeze > requirement.txt
```

---

## 📞 Still Having Issues?

Tell me:
1. **What specific error do you see?** (Copy the exact error message)
2. **When does it happen?** (During setup, testing, etc.)
3. **What step are you on?** (Initial setup, database, running, testing, etc.)
4. **What's your Python version?** (`python --version`)
5. **What OS?** (Windows, Mac, Linux)

I'll help you fix it! 🚀
