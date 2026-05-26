# PG Finder - Setup & Configuration Guide

## 🎯 Project Overview

**PG Finder** is a complete Django-based accommodation management system for Paying Guest (PG) listings with:
- User authentication (Seeker & Owner)
- PG listing CRUD operations
- Real-time chat system
- Payment integration (Razorpay)
- Rating & Review system
- Booking management
- Notification system

---

## ⚙️ Installation & Setup

### 1. **Environment Variables** (.env file)
Create a `.env` file in the project root with the following variables:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@pgfinder.com

# Google Maps API
GOOGLE_MAPS_EMBED_API_KEY=your-google-maps-api-key

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx OR rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-secret-key

# Database (if using PostgreSQL)
DB_NAME=pgfinder_db
DB_USER=pgfinder_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 2. **Install Dependencies**
```bash
pip install -r requirement.txt
```

### 3. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 💳 Razorpay Integration Guide

### **Step 1: Get Razorpay Keys**

1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Sign up or log in
3. Navigate to **Settings** → **API Keys**
4. Copy your **Key ID** and **Key Secret**
5. Add them to your `.env` file

### **Step 2: Test Mode vs Live Mode**

**Test Keys** (for development):
- Start with `rzp_test_`
- Use test card numbers for testing

**Live Keys** (for production):
- Start with `rzp_live_`
- Use real payment methods

### **Step 3: Test Payment Flow**

**Test Cards:**
```
Success Card:
Number: 4111 1111 1111 1111
Expiry: Any future date (MM/YY)
CVV: Any 3 digits

Failure Card:
Number: 4222 2222 2222 2222
```

---

## 🔐 Payment Security

### **Built-in Security Features:**

1. **Signature Verification**: All payments verified using HMAC-SHA256
2. **Webhook Validation**: Razorpay webhooks verified for authenticity
3. **CSRF Protection**: All payment forms CSRF-protected
4. **SSL/TLS**: Payment page served over HTTPS
5. **PCI Compliance**: Sensitive data not stored locally

### **Payment Flow:**
```
User Clicks Pay
    ↓
Create Razorpay Order (Backend)
    ↓
Display Razorpay Checkout (Frontend)
    ↓
User Completes Payment
    ↓
Verify Signature (Backend)
    ↓
Update Booking Status
    ↓
Create Notification
```

---

## 📝 Forms Created

### **Authentication Forms** (`users/forms.py`)
1. **RegisterForm** - User registration
2. **LoginForm** - Email/Username login
3. **ProfileEditForm** - Edit profile details
4. **ChangePasswordForm** - Change password

### **PG Forms** (`pgs/forms.py`)
1. **AddPGForm** - Create new PG listing
2. **EditPGForm** - Edit existing PG
3. **PGImageForm** - Upload PG images
4. **RatingForm** - Rate a PG (1-5 stars)
5. **ReviewForm** - Write a review

### **Payment Forms** (`pgs/payment_forms.py`)
1. **RazorpayPaymentForm** - Payment verification
2. **PaymentVerificationForm** - Webhook verification

---

## 🔗 API Endpoints

### **Payment Endpoints**
```
POST   /pgs/payment/initiate/<booking_id>/    → Initiate payment
POST   /pgs/payment/verify/<booking_id>/       → Verify payment signature
POST   /pgs/payment/webhook/                   → Razorpay webhook handler
GET    /pgs/payment/status/<booking_id>/       → Check payment status
POST   /pgs/payment/refund/<booking_id>/       → Request refund
```

### **PG Endpoints**
```
GET    /pgs/                                    → List all PGs
GET    /pgs/<slug>/                            → PG details
POST   /pgs/pgregister/                        → Register new PG (Owner)
GET    /pgs/book/<slug>/                       → View booking form
POST   /pgs/book/<slug>/                       → Create booking
GET    /pgs/saved/                             → Saved PGs list
```

### **User Endpoints**
```
GET    /user/login/                            → Login page
POST   /user/register/                         → User registration
GET    /user/logout/                           → Logout
GET    /user/profile/                          → User profile
```

---

## 📊 Database Models Summary

### **Core Models**
- **MyUser** - Custom user model
- **PgListing** - PG property listing
- **PGImage** - PG images
- **Booking** - Booking records
- **Payment** - Payment transactions
- **Rating** - Star ratings
- **Review** - Text reviews
- **ChatConversation** - Chat threads
- **ChatMessage** - Chat messages
- **Notification** - System notifications
- **VisitRequest** - Visit requests
- **SavedPg** - Saved listings

---

## 🚀 Deployment Checklist

### **Before Going Live:**

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper static files serving
- [ ] Configure email backend for production
- [ ] Switch to live Razorpay keys
- [ ] Configure HTTPS/SSL
- [ ] Set secure cookies and CSRF settings
- [ ] Configure Django security middleware
- [ ] Set up monitoring and logging
- [ ] Configure backups and disaster recovery

### **Environment Variables for Production:**
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-live-secret-key
```

---

## 🧪 Testing Payment Integration

### **Manual Testing Steps:**

1. **Create Test Booking:**
   - Create a PG listing as owner
   - Book it as a user
   - Go to booking confirmation page

2. **Initiate Payment:**
   - Click "Pay Now" button
   - Should redirect to Razorpay checkout

3. **Complete Test Payment:**
   - Use test card: `4111 1111 1111 1111`
   - Enter any future expiry date
   - Enter any CVV
   - Payment should succeed

4. **Verify Payment:**
   - Check if booking status changed to "confirmed"
   - Check if notification was created
   - Verify payment record in admin panel

### **Automated Testing (Unit Tests):**

Create `tests.py`:
```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from pgs.models import PgListing, Booking, Payment
from datetime import date

User = get_user_model()

class PaymentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            date_of_birth=date(2000, 1, 1),
            phone='9999999999'
        )

    def test_payment_creation(self):
        # Test payment record creation
        pass

    def test_signature_verification(self):
        # Test Razorpay signature verification
        pass
```

---

## 📱 Frontend Integration

### **Payment Button Template Code:**
```html
<!-- In your booking confirmation template -->
<a href="{% url 'initiate_payment' booking.id %}" class="btn btn-primary">
    💳 Proceed to Payment
</a>
```

### **Check Payment Status:**
```javascript
fetch('/pgs/payment/status/{{ booking_id }}/')
    .then(response => response.json())
    .then(data => {
        console.log('Payment Status:', data.status);
    });
```

---

## 🐛 Troubleshooting

### **Common Issues:**

#### **Issue: "Razorpay Key ID not configured"**
- ✅ **Solution**: Add Razorpay keys to .env file
- ✅ **Verify**: `python manage.py shell` → `from django.conf import settings` → `print(settings.RAZORPAY_KEY_ID)`

#### **Issue: "Payment verification failed"**
- ✅ **Solution**: Ensure key secret is correct
- ✅ **Check**: Test mode vs live mode keys
- ✅ **Verify**: Signature generation logic

#### **Issue: "Webhook not processing"**
- ✅ **Solution**: Configure webhook URL in Razorpay dashboard
- ✅ **URL**: `https://yourdomain.com/pgs/payment/webhook/`
- ✅ **Method**: POST
- ✅ **Enable**: payment.authorized, payment.failed, order.paid events

#### **Issue: "CSRF token missing"**
- ✅ **Solution**: Ensure {% csrf_token %} in forms
- ✅ **Check**: CSRF middleware enabled in settings

---

## 📚 Additional Resources

- [Razorpay Documentation](https://razorpay.com/docs/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django Channels for Chat](https://channels.readthedocs.io/)
- [Google Maps API](https://developers.google.com/maps)

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Razorpay dashboard for payment details
3. Check Django logs for errors
4. Enable DEBUG mode temporarily to see detailed error messages

---

**Last Updated**: March 2026
**Version**: 1.0
**Django Version**: 5.2.6
**Python Version**: 3.x

