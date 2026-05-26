# PG Finder - Quick Start Guide

## 🚀 Get Started in 5 Minutes!

### Step 1: Start the Application

#### Option A: Using Daphne (Recommended for Chat/WebSocket Support)
```bash
cd d:\Pg_finder
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application
```

#### Option B: Using Django Development Server
```bash
cd d:\Pg_finder
python manage.py runserver
```

The application will be available at: **http://localhost:8000**

### Step 2: Login with Test Accounts

#### Admin Account
- **URL**: http://localhost:8000/admin/
- **Username**: admin@pgfinder.com
- **Password**: admin123
- **Purpose**: Manage listings, payments, users, and reviews

#### Owner Account
- **Username**: owner1
- **Password**: owner123
- **Purpose**: Create and manage PG listings

#### Tenant Account
- **Username**: tenant1
- **Password**: tenant123
- **Purpose**: Browse PGs, make bookings, join chat

### Step 3: Test the Features

#### Browse PGs
1. Open http://localhost:8000/pgs/
2. View available listings
3. Click on any PG to see details

#### Advanced Search
1. Go to http://localhost:8000/pgs/advanced-search/
2. Filter by location, price, amenities
3. View results on map

#### Make a Booking
1. Login as tenant1
2. Click "Book Now" on any PG
3. Select your check-in date
4. Confirm booking

#### Test Payment (PhonePe UPI)
1. After booking, click "Proceed to UPI Payment"
2. You'll see:
   - QR code for UPI payment
   - UPI ID to copy and use
   - Real-time payment status checker
3. In development, payment status auto-updates (test mode)

#### Chat System
1. Login as tenant1
2. Click on any PG
3. Click "Start Chat" button
4. Real-time messaging with owner (WebSocket)
5. Demo features:
   - Message sending/receiving
   - Typing indicators
   - Read receipts
   - User blocking

#### Ratings & Reviews
1. Login as tenant1
2. Go to any PG
3. Click "Rate this PG"
4. Give a 5-star rating
5. Write a review
6. Admin can approve reviews

---

## 📊 Initial Sample Data

The following test data is ready to use:

### PG Listings
- **Cozy 1BHK in Bangalore** (Boys, Single, ₹15,000/month)
- **Girls PG near Whitefield** (Girls, Double, ₹12,000/month)

### Bookings
- Test booking created for tenant1 at first PG
- Ready to proceed to payment

### Chat
- Sample conversation between tenant and owner
- Test messages already created

---

## 🔐 Environment Configuration

Your `.env` file is configured with:
- **Database**: SQLite (local file: `db.sqlite3`)
- **Email**: Console backend (logs to console, no SMTP needed)
- **PhonePe**: SANDBOX mode (for testing)
- **Debug**: True (development mode)

### For Production Setup, See:
- **Full Deployment Guide**: `SETUP_AND_DEPLOYMENT_GUIDE.md`
- **PhonePe Configuration**: Use real credentials in `.env`
- **Database**: Switch to PostgreSQL
- **Email**: Configure real SMTP server

---

## 📱 Key URLs

| Feature | URL |
|---------|-----|
| **Home** | http://localhost:8000/ |
| **Admin** | http://localhost:8000/admin/ |
| **PG Listings** | http://localhost:8000/pgs/ |
| **Advanced Search** | http://localhost:8000/pgs/advanced-search/ |
| **Map View** | http://localhost:8000/pgs/map/ |
| **Chat** | http://localhost:8000/chat/ |
| **My Bookings** | http://localhost:8000/pgs/my-bookings/ |

---

## 🧪 Test Payment Flow

### In Development (No Real Payment Needed)

1. **Create Booking**
   - Login as tenant1
   - Book a PG
   - Payment status = "pending"

2. **View Payment Page**
   - Click "Proceed to UPI Payment"
   - See QR code + UPI ID
   - Status polling starts automatically

3. **Test Payment Update**
   - Go to Admin Panel
   - Navigate to Payments
   - Manually change payment status to "completed"
   - Frontend automatically detects change
   - Booking status updates to "confirmed"

### With Real PhonePe Account

1. Get PhonePe merchant credentials
2. Update `.env` with credentials
3. Change PHONEPE_ENVIRONMENT to SANDBOX
4. Follow PhonePe test flow
5. Real payment will process automatically

---

## 🛠️ Useful Management Commands

```bash
# Run migrations
python manage.py migrate

# Check for issues
python manage.py check

# Create admin
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Access Django shell
python manage.py shell

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json
```

---

## 🐛 Troubleshooting

### Issue: Port 8000 Already in Use
```bash
# Use different port
python manage.py runserver 8001
# Or
daphne -b 0.0.0.0 -p 8001 PgFinder.asgi:application
```

### Issue: Database Error
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py shell < create_test_data.py
```

### Issue: Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Issue: Chat/WebSocket Not Working
- Make sure you're using Daphne, not Django's runserver
- Check browser console for WebSocket errors
- Ensure Redis is running (if using Redis backend)

---

## 📚 Feature Overview

### User Management ✅
- User registration and authentication
- User profiles
- Owner and Tenant roles

### PG Listings ✅
- Create, edit, delete listings
- Upload multiple images
- Manage amenities and facilities
- Set availability

### Search & Discovery ✅
- Advanced filters (location, price, amenities)
- Google Maps integration
- Save favorite PGs
- Visit requests

### PhonePe UPI Payment ✅
- QR code generation
- Direct UPI transfer
- Real-time status polling
- Automatic confirmation
- Refund support

### Real-Time Chat ✅
- WebSocket-based messaging
- Typing indicators
- Read receipts
- User blocking
- Chat history

### Ratings & Reviews ✅
- 5-star rating system
- Detailed reviews
- Admin moderation
- User feedback

### Notifications ✅
- Real-time alerts
- Payment notifications
- Booking updates
- Chat messages

---

## 🚀 Next Steps

After testing locally:

1. **Set Up PostgreSQL** (for production)
   - Better performance
   - Scalability
   - Backup capabilities

2. **Configure Real Email** (for notifications)
   - Gmail or custom SMTP
   - Payment confirmations
   - Booking notifications

3. **Add Google Maps API Key** (for production)
   - Real location viewing
   - Advanced map features

4. **Register with PhonePe** (for real payments)
   - Get merchant credentials
   - Test with SANDBOX
   - Deploy to PRODUCTION

5. **Deploy to Production**
   - Choose hosting (Heroku, AWS, DigitalOcean)
   - Configure SSL/HTTPS
   - Set up reverse proxy
   - Enable Redis for chat
   - Monitor and scale

---

## 📖 Documentation

- **Full Setup Guide**: See `SETUP_AND_DEPLOYMENT_GUIDE.md`
- **API Documentation**: See code comments in views.py
- **Database Schema**: Check models.py files
- **Requirements**: See `requirement.txt`

---

## 💡 Tips & Tricks

### Test Multiple Users
```bash
# Create more test accounts
python manage.py shell
>>> from users.models import MyUser
>>> MyUser.objects.create_user('testuser', 'test@example.com', 'password123')
```

### View Database
```bash
# Use SQLite browser or command line
sqlite3 db.sqlite3
sqlite> .tables
sqlite> SELECT * FROM auth_user;
```

### Debug Payment Issues
```bash
# Check payment logs
tail -f console_output.log
# View in admin
http://localhost:8000/admin/pgs/payment/
```

### Monitor WebSocket
```bash
# Browser DevTools → Network → WS
# Check WebSocket connections
# View message flow
```

---

## ✨ Ready to Go!

Your PG Finder application is **fully configured and ready to use**.

**Start the server now and begin exploring!**

```bash
daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application
```

Then open: **http://localhost:8000**

---

**Questions?** Check the full guide: `SETUP_AND_DEPLOYMENT_GUIDE.md`

**Issues?** See Troubleshooting section above.

**Last Updated**: 2026-03-24
**Version**: 1.0.0 - Production Ready
