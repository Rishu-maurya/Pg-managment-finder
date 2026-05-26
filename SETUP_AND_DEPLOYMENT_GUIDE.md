# PG Finder - Complete Setup & Deployment Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Database Setup](#database-setup)
8. [Testing the Payment System](#testing-the-payment-system)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)
11. [API Endpoints](#api-endpoints)

---

## Project Overview

**PG Finder** is a comprehensive Django-based platform for finding, managing, and booking Paying Guest (PG) accommodations. It includes:

- ✅ **User Authentication & Authorization** - Registration, login, role-based access
- ✅ **PG Listing Management** - Create, update, delete PG listings with images
- ✅ **Advanced Search & Filters** - Find PGs by location, price, amenities, etc.
- ✅ **Real-Time Chat System** - WebSocket-based messaging between users
- ✅ **PhonePe UPI Payment** - Automatic payment processing with QR code generation
- ✅ **Google Maps Integration** - View PG locations on interactive maps
- ✅ **Booking Management** - Create and manage PG bookings
- ✅ **Ratings & Reviews** - Rate and review PG accommodations
- ✅ **Notifications System** - Real-time notifications for events

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Django | 5.2.6 |
| **Language** | Python | 3.x |
| **Database** | SQLite (dev), PostgreSQL (prod) | Latest |
| **Real-Time** | Django Channels | 4.1.0 |
| **ASGI Server** | Daphne | 4.1.2 |
| **Payment** | PhonePe API | v1.0 |
| **Maps** | Google Maps API | Latest |
| **Frontend** | Bootstrap 5, jQuery | Latest |
| **Cache** | Redis | Latest |

---

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip package manager
- Virtual environment (venv)
- Git for version control

### Optional (for production)
- PostgreSQL 12+
- Redis server
- Nginx or Apache web server
- Supervisor for process management
- SSL certificate (Let's Encrypt)

---

## Installation & Setup

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd Pg_finder
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirement.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your editor
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user. Example:
```
Username: admin
Email: admin@pgfinder.com
Password: ••••••••
```

---

## Configuration

### Environment Variables (.env file)

#### Essential Configuration
```env
# Django
DEBUG=True                              # Set to False in production
SECRET_KEY=your-secret-key-here         # Generate a strong key
ALLOWED_HOSTS=localhost,127.0.0.1       # Add your domain in production

# Database
DATABASE_URL=sqlite:///db.sqlite3       # SQLite for dev
# DATABASE_URL=postgresql://user:pass@localhost/pgfinder  # PostgreSQL for prod

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# PhonePe Payment Gateway
PHONEPE_MERCHANT_ID=your-merchant-id
PHONEPE_API_KEY=your-api-key
PHONEPE_API_SECRET=your-api-secret
PHONEPE_ENVIRONMENT=SANDBOX             # Use SANDBOX for testing
```

#### PhonePe Setup
1. Register at [PhonePe Business](https://business.phonepe.in/)
2. Get your merchant credentials
3. Add credentials to .env file
4. Test with SANDBOX environment first

---

## Running the Application

### Development Server (SQLite + In-Memory Chat)

#### Option 1: Using Django Development Server
```bash
python manage.py runserver
```
Access at: `http://localhost:8000`

#### Option 2: Using Daphne (with WebSocket support)
```bash
# Install Daphne if not already installed
pip install daphne

# Run Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application
```
Access at: `http://localhost:8000`

### Development Server (with Redis)

#### Step 1: Install Redis
```bash
# Windows (using Chocolatey)
choco install redis

# Linux
sudo apt-get install redis-server

# Mac
brew install redis
```

#### Step 2: Start Redis Server
```bash
# Windows
redis-server

# Linux/Mac
redis-server
```

#### Step 3: Run Django with Daphne
```bash
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application
```

### Access Admin Panel
- URL: `http://localhost:8000/admin/`
- Username: Your superuser username
- Password: Your superuser password

---

## Database Setup

### SQLite (Development)
- Default database (no setup needed)
- Located at: `db.sqlite3`
- Perfect for development and testing

### PostgreSQL (Production)

#### Installation
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb pgfinder
sudo -u postgres createuser pgfinder_user
sudo -u postgres psql -c "ALTER USER pgfinder_user WITH PASSWORD 'strong_password';"
```

#### Configuration
Update `.env`:
```env
DATABASE_URL=postgresql://pgfinder_user:strong_password@localhost:5432/pgfinder
```

#### Run Migrations
```bash
python manage.py migrate
```

---

## Testing the Payment System

### PhonePe Payment Flow (SANDBOX Mode)

#### Step 1: Create a Test Booking
1. Register as a new user
2. Browse PG listings
3. Click "Book Now" on a listing
4. Enter check-in date and confirm booking

#### Step 2: Initiate Payment
1. Click "Proceed to UPI Payment"
2. You'll see QR code and UPI ID

#### Step 3: Simulate Payment
```bash
# Use PhonePe's sandbox test gateway
# Follow PhonePe's testing documentation
# Or use their test credentials
```

#### Step 4: Verify Payment
- Payment status will update automatically every 5 seconds
- Booking will be confirmed on successful payment
- Check admin panel: `/admin/pgs/payment/`

### Testing Without Real PhonePe Account

For development, you can test the payment flow:
1. Create a booking
2. Click payment button
3. Frontend will poll status endpoint
4. Manually update payment status in admin panel

---

## Deployment Guide

### Using Heroku

#### Step 1: Install Heroku CLI
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
heroku login
```

#### Step 2: Create Heroku App
```bash
heroku create your-app-name
```

#### Step 3: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

#### Step 4: Configure Environment Variables
```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-production-secret-key
heroku config:set PHONEPE_MERCHANT_ID=your-merchant-id
# Add other required variables
```

#### Step 5: Create Procfile
Create file `Procfile`:
```
web: daphne -b 0.0.0.0 -p $PORT PgFinder.asgi:application
```

#### Step 6: Deploy
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Using AWS EC2

#### Step 1: Setup EC2 Instance
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib nginx supervisor
```

#### Step 2: Setup Application
```bash
cd /var/www
git clone <your-repo>
cd Pg_finder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

#### Step 3: Configure Nginx
Create `/etc/nginx/sites-available/pgfinder`:
```nginx
upstream pgfinder {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://pgfinder;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/Pg_finder/staticfiles/;
    }
}
```

#### Step 4: Configure Supervisor
Create `/etc/supervisor/conf.d/pgfinder.conf`:
```ini
[program:pgfinder]
directory=/var/www/Pg_finder
command=/var/www/Pg_finder/.venv/bin/daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/pgfinder.err.log
stdout_logfile=/var/log/pgfinder.out.log
```

---

## Troubleshooting

### Common Issues

#### 1. PhonePe API Connection Failed
```
Error: Failed to connect to PhonePe API
```
**Solution:**
- Verify PHONEPE_MERCHANT_ID and credentials in .env
- Check internet connection
- Ensure PHONEPE_ENVIRONMENT is correct (SANDBOX for testing)
- Check PhonePe API status

#### 2. WebSocket Connection Failed
```
WebSocket connection failed
```
**Solution:**
- Use Daphne instead of Django's runserver
- Ensure Redis is running (if using Redis backend)
- Check browser console for detailed errors
- Verify WebSocket URL is correct

#### 3. Database Migration Error
```
Error: no such table: pgs_payment
```
**Solution:**
```bash
python manage.py migrate --run-syncdb
python manage.py migrate pgs
```

#### 4. Static Files Not Found
**Solution:**
```bash
python manage.py collectstatic --noinput
```

#### 5. Email Not Sending
**Solution:**
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Enable "Less secure app access" for Gmail
- Or use app-specific password for Gmail
- Check SMTP settings in .env

---

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration
- `GET /api/auth/profile/` - Get user profile

### PG Listings
- `GET /pgs/` - List all PGs
- `POST /pgs/pgregister/` - Create new PG listing
- `GET /pgs/<slug>/` - Get PG details
- `PUT /pgs/<slug>/` - Update PG listing
- `DELETE /pgs/<slug>/` - Delete PG listing

### Search & Filter
- `GET /pgs/advanced-search/` - Advanced search with filters
- `GET /pgs/map/` - View PGs on map
- `GET /pgs/api/map-markers/` - Get map markers (JSON)

### Bookings
- `POST /pgs/book/<slug>/` - Create booking
- `GET /pgs/my-bookings/` - List user's bookings
- `GET /pgs/booking-confirmation/<id>/` - Booking confirmation page
- `POST /pgs/cancel-booking/<id>/` - Cancel booking

### Payment
- `POST /pgs/payment/initiate/<id>/` - Initiate PhonePe payment
- `POST /pgs/payment/verify/<id>/` - Verify payment
- `GET /pgs/payment/status/<id>/` - Check payment status (JSON)
- `POST /pgs/payment/refund/<id>/` - Request refund
- `POST /pgs/payment/webhook/` - PhonePe webhook endpoint

### Chat (WebSocket)
- `ws://localhost:8000/ws/chat/conversation/<id>/` - Chat WebSocket
- `ws://localhost:8000/ws/notifications/` - Notifications WebSocket

### Chat (HTTP)
- `GET /chat/` - List conversations
- `GET /chat/conversation/<id>/` - Get conversation
- `POST /chat/start/<user_id>/` - Start chat with user
- `POST /chat/block/<id>/` - Block user
- `POST /chat/unblock/<id>/` - Unblock user

---

## Project Structure

```
Pg_finder/
├── PgFinder/               # Main project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration (WebSocket)
│
├── pgs/                    # PG listings & bookings app
│   ├── models.py           # PG, Booking, Payment models
│   ├── views.py            # PG views
│   ├── payment_views.py    # Payment processing
│   ├── urls.py             # PG URL routes
│   └── admin.py            # Admin configuration
│
├── users/                  # User authentication app
│   ├── models.py           # User, Profile models
│   ├── views.py            # Auth views
│   └── forms.py            # Auth forms
│
├── chat/                   # Real-time chat app
│   ├── consumers.py        # WebSocket consumers
│   ├── views.py            # Chat views
│   ├── routing.py          # WebSocket routing
│   └── models.py           # Chat models
│
├── contact/                # Contact & support app
│   ├── models.py           # Contact form
│   └── views.py            # Contact view
│
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── pgs/                # PG templates
│   ├── users/              # User templates
│   └── chat/               # Chat templates
│
├── static/                 # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
│
├── .env                    # Environment variables (local)
├── .env.example            # Environment variables (template)
├── requirement.txt         # Python dependencies
├── manage.py               # Django management
└── README.md               # This file
```

---

## Key Features Implemented

### 1. User Management
- User registration and authentication
- User profiles with avatar and contact info
- Role-based access (Tenant, Owner, Admin)

### 2. PG Listings
- Create, update, delete PG listings
- Multiple images per PG
- Amenities and facilities management
- Availability tracking

### 3. Search & Discovery
- Advanced search with filters (location, price, amenities)
- Google Maps integration for location viewing
- Save favorite PGs
- Visit requests

### 4. PhonePe UPI Payment
- QR code generation for payments
- Direct UPI ID transfer option
- Real-time payment status polling
- Automatic booking confirmation
- Refund processing

### 5. Real-Time Chat
- WebSocket-based messaging
- User blocking and unblocking
- Typing indicators
- Message read receipts
- Chat history

### 6. Ratings & Reviews
- 5-star rating system
- Detailed reviews with moderation
- User-based rating tracking

### 7. Notifications
- Real-time notifications
- Payment notifications
- Booking notifications
- Chat notifications

---

## Support & Documentation

### Admin Panel
Access comprehensive admin interface at:
```
http://localhost:8000/admin/
```

Features:
- User management
- PG listing management
- Payment tracking and history
- Booking status management
- Rating and review moderation
- Chat message monitoring

### Useful Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Create test data
python manage.py shell
>>> from pgs.models import PgListing
>>> PgListing.objects.create(...)

# Check for issues
python manage.py check

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py clear_cache

# Dump database
python manage.py dumpdata > backup.json

# Load database
python manage.py loaddata backup.json
```

---

## Next Steps

1. ✅ Copy `.env.example` to `.env` and update credentials
2. ✅ Install dependencies: `pip install -r requirement.txt`
3. ✅ Run migrations: `python manage.py migrate`
4. ✅ Create superuser: `python manage.py createsuperuser`
5. ✅ Start development server: `daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application`
6. ✅ Access application: `http://localhost:8000`
7. ✅ Access admin: `http://localhost:8000/admin/`

---

## License

This project is licensed under the MIT License.

---

**For issues, questions, or contributions, please create an issue or pull request on GitHub.**

Last Updated: 2026-03-24
Version: 1.0.0
Status: ✅ Production Ready
