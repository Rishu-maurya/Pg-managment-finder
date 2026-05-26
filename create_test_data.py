#!/usr/bin/env python
"""
Create sample/test data for PG Finder application.
Run with: python manage.py shell < create_test_data.py
Or: python create_test_data.py
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PgFinder.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import MyUser, Notification
from pgs.models import PgListing, PGImage, SavedPg, Booking, Rating, Review, Payment
from chat.models import ChatConversation, ChatMessage

print("🚀 Creating Test Data for PG Finder...")

# 1. Create Test Users
print("\n📝 Creating test users...")

# Create Admin User
admin_user, created = MyUser.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@pgfinder.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'phone': '9999999999',
        'is_owner': False,
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✅ Created admin user")

# Create Test Owner
owner_user, created = MyUser.objects.get_or_create(
    username='owner1',
    defaults={
        'email': 'owner1@pgfinder.com',
        'first_name': 'Rajesh',
        'last_name': 'Kumar',
        'phone': '9876543210',
        'is_owner': True,
        'is_staff': False,
        'is_superuser': False,
    }
)
if created:
    owner_user.set_password('owner123')
    owner_user.save()
    print(f"✅ Created owner user: {owner_user.username}")

# Create Test Tenant
tenant_user, created = MyUser.objects.get_or_create(
    username='tenant1',
    defaults={
        'email': 'tenant1@pgfinder.com',
        'first_name': 'Rahul',
        'last_name': 'Singh',
        'phone': '9123456789',
        'is_owner': False,
        'is_staff': False,
        'is_superuser': False,
    }
)
if created:
    tenant_user.set_password('tenant123')
    tenant_user.save()
    print(f"✅ Created tenant user: {tenant_user.username}")

# 2. Create PG Listings
print("\n🏢 Creating test PG listings...")

pg_data = [
    {
        'title': 'Cozy 1BHK in Bangalore',
        'description': 'Modern 1 bedroom apartment near Indiranagar metro station. Fully furnished with AC, WiFi, and water supply.',
        'address': '123 Indiranagar Main Road',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'pin_code': '560038',
        'price_per_month': 15000,
        'security_deposit': 30000,
        'type_of_pg': 'boys',
        'sharing_type': 'single',
        'furnishing_status': 'fully_furnished',
        'food_available': True,
        'parking_available': True,
        'wifi_available': True,
        'amenities': 'WiFi, AC, Parking, Laundry, Food',
    },
    {
        'title': 'Girls PG near Whitefield',
        'description': 'Safe and secure PG for girls. Located near Whitefield IT hub with good connectivity.',
        'address': '456 Whitefield Main Street',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'pin_code': '560066',
        'price_per_month': 12000,
        'security_deposit': 24000,
        'type_of_pg': 'girls',
        'sharing_type': 'double',
        'furnishing_status': 'fully_furnished',
        'food_available': True,
        'parking_available': False,
        'wifi_available': True,
        'amenities': 'WiFi, Washing Machine, Food, 24/7 Security',
    },
    {
        'title': 'Budget PG in Koramangala',
        'description': 'Affordable budget PG in the heart of Koramangala. Perfect for students and startup professionals.',
        'address': '789 Koramangala 1st Block',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'pin_code': '560034',
        'price_per_month': 8000,
        'security_deposit': 16000,
        'type_of_pg': 'coed',
        'sharing_type': 'triple',
        'furnishing_status': 'semi_furnished',
        'food_available': False,
        'parking_available': False,
        'wifi_available': True,
        'amenities': 'WiFi, Common Kitchen, Common Hall',
    },
]

pg_objects = []
for data in pg_data:
    pg, created = PgListing.objects.get_or_create(
        title=data['title'],
        owner=owner_user,
        defaults={
            **data,
            'available_from': datetime.now().date(),
            'slug': data['title'].lower().replace(' ', '-'),
        }
    )
    if created:
        print(f"✅ Created PG: {pg.title}")
    pg_objects.append(pg)

# Set availability
for pg in pg_objects:
    pg.is_available = True
    pg.save()

# 3. Create Bookings
print("\n📅 Creating test bookings...")

check_in = (datetime.now() + timedelta(days=7)).date()
booking, created = Booking.objects.get_or_create(
    tenant=tenant_user,
    pg=pg_objects[0],
    defaults={
        'check_in_date': check_in,
        'amount': 15000,
        'status': 'pending',
    }
)
if created:
    print(f"✅ Created booking: {booking.id}")

# 4. Create Payment Record
print("\n💳 Creating test payment record...")

payment, created = Payment.objects.get_or_create(
    booking=booking,
    defaults={
        'amount': 15000,
        'payment_status': 'pending',
        'payment_method': 'upi',
        'phonepe_order_id': 'order_test_123',
    }
)
if created:
    print(f"✅ Created payment record")

# 5. Create Ratings and Reviews
print("\n⭐ Creating test ratings and reviews...")

rating, created = Rating.objects.get_or_create(
    user=tenant_user,
    pg=pg_objects[0],
    defaults={
        'rating': 4,
    }
)
if created:
    print(f"✅ Created rating")

review, created = Review.objects.get_or_create(
    user=tenant_user,
    pg=pg_objects[0],
    rating=rating,
    defaults={
        'title': 'Great PG with excellent facilities',
        'content': 'The PG is well-maintained, has good food, and friendly management. WiFi is consistent. Highly recommended!',
        'is_approved': True,
    }
)
if created:
    print(f"✅ Created review")

# 6. Create Saved PGs
print("\n❤️ Creating saved PGs...")

for pg in pg_objects[:2]:
    saved_pg, created = SavedPg.objects.get_or_create(
        user=tenant_user,
        pg=pg,
    )
    if created:
        print(f"✅ Saved PG: {pg.title}")

# 7. Create Chat Conversation
print("\n💬 Creating test chat conversation...")

conversation, created = ChatConversation.objects.get_or_create(
    user1=tenant_user,
    user2=owner_user,
    defaults={
        'pg': pg_objects[0],
    }
)
if created:
    print(f"✅ Created chat conversation")

    # Add sample messages
    ChatMessage.objects.create(
        conversation=conversation,
        sender=tenant_user,
        content='Hi, is this PG still available?'
    )
    ChatMessage.objects.create(
        conversation=conversation,
        sender=owner_user,
        content='Yes, it\'s available. When would you like to visit?'
    )
    print(f"✅ Added sample messages")

# 8. Create Notifications
print("\n🔔 Creating test notifications...")

notification, created = Notification.objects.get_or_create(
    user=tenant_user,
    notification_type='booking_created',
    defaults={
        'title': 'Booking Created',
        'message': 'Your booking has been created successfully. Proceed to payment.',
        'booking_id': booking.id,
        'pg_id': pg_objects[0].id,
    }
)
if created:
    print(f"✅ Created notification")

print("\n" + "="*50)
print("✅ TEST DATA CREATION COMPLETED!")
print("="*50)

print("\n📋 Test Accounts Created:")
print("  Admin User:")
print("    Username: admin")
print("    Password: admin123")
print("\n  Owner User:")
print("    Username: owner1")
print("    Password: owner123")
print("\n  Tenant User:")
print("    Username: tenant1")
print("    Password: tenant123")

print("\n🌍 Access URLs:")
print("  Website: http://localhost:8000/")
print("  Admin: http://localhost:8000/admin/")
print("  PG List: http://localhost:8000/pgs/")

print("\n💡 Next Steps:")
print("  1. Start the server: daphne -b 0.0.0.0 -p 8000 PgFinder.asgi:application")
print("  2. Login with test accounts")
print("  3. Test the payment flow")
print("  4. Verify chat system")
print("  5. Test search and filters")

print("\n✨ Setup Complete!")
