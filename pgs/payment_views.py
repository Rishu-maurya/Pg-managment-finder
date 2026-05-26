"""
Razorpay Payment Gateway Integration for PG Finder - Complete Automated Flow

Features:
- Instant order creation
- Secure client-side checkout
- Server-side payment verification
- Webhook for async events
- Full error handling and notifications

Test Card: 4111 1111 1111 1111 | CVV: 111 | Expiry: Any future date
"""

import razorpay
import json
from decimal import Decimal
import logging
from uuid import uuid4
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

from .models import Booking, Payment
from users.models import Notification

logger = logging.getLogger(__name__)

# Razorpay Client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


@login_required(login_url='user_login')
@require_http_methods(['GET'])
def initiate_payment(request, booking_id):
    """Create Razorpay order and render checkout page"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)

    # Check if booking already has a completed payment
    payment = getattr(booking, 'payment', None)
    if payment and payment.payment_status == 'completed':
        messages.warning(request, 'Payment already completed.')
        return redirect('booking_confirmation', booking_id=booking_id)

    # Get or create payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.amount,
            'payment_status': 'pending',
            'payment_method': 'upi',
        }
    )

    # If payment already has an order ID, redirect to checkout
    if payment.razorpay_order_id:
        context = {
            'booking': booking,
            'payment': payment,
            'order_id': payment.razorpay_order_id,
            'key': settings.RAZORPAY_KEY_ID,
            'amount': booking.amount,
            'currency': 'INR',
            'name': 'PG Finder',
            'description': f"Payment for {booking.pg.title}",
            'prefill': {
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
                'contact': getattr(request.user, 'phone', ''),
            }
        }
        return render(request, 'pgs/payment/razorpay_checkout.html', context)

    try:
        # Create Razorpay order
        amount_paise = int(booking.amount * Decimal('100'))  # Use Decimal for currency precision
        order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1, # Auto-capture payment on success
            'receipt': f"booking_{booking.id}_{uuid4().hex[:8]}",
            'notes': {
                'booking_id': booking.id,
                'tenant': request.user.email,
                'pg_title': booking.pg.title,
            }
        })

        payment.razorpay_order_id = order['id']
        payment.save(update_fields=['razorpay_order_id'])

        context = {
            'booking': booking,
            'payment': payment,
            'order_id': order['id'],
            'key': settings.RAZORPAY_KEY_ID,
            'amount': booking.amount,
            'currency': 'INR',
            'name': 'PG Finder',
            'description': f"Payment for {booking.pg.title}",
            'prefill': {
                'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'email': request.user.email,
                'contact': getattr(request.user, 'phone', ''),
            }
        }

        return render(request, 'pgs/payment/razorpay_checkout.html', context)

    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        messages.error(request, 'Payment initiation failed. Please try again.')
        return redirect('booking_confirmation', booking_id=booking_id)


@require_POST
@login_required
def razorpay_verify_payment(request, booking_id):
    """Server-side verification after payment"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    amount_paise = int(booking.amount * Decimal('100'))
    payment = getattr(booking, 'payment', None)

    if not payment:
        messages.error(request, 'Payment record not found.')
        return redirect('booking_confirmation', booking_id=booking_id)

    try:
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Security check: Ensure order ID matches our database record
        if razorpay_order_id != payment.razorpay_order_id:
            messages.error(request, 'Invalid transaction session.')
            return redirect('booking_confirmation', booking_id=booking.id)

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }

        # Verify payment signature using Razorpay official utility
        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            payment.payment_status = 'failed'
            payment.error_message = 'Signature verification failed'
            payment.save()
            messages.error(request, 'Payment verification failed.')
            return redirect('booking_confirmation', booking_id=booking.id)

        # Fetch payment details from Razorpay
        rzp_payment = client.payment.fetch(razorpay_payment_id)

        # Security check: Amount mismatch
        if rzp_payment['amount'] != amount_paise:
            messages.error(request, 'Payment amount mismatch detected.')
            return redirect('booking_confirmation', booking_id=booking.id)

        if rzp_payment['status'] in ['captured', 'authorized']:
            # Handle 'authorized' status by capturing it manually if needed
            if rzp_payment['status'] == 'authorized':
                client.payment.capture(razorpay_payment_id, amount_paise)

            # Update actual payment method used
            rzp_method = rzp_payment.get('method', 'other')
            if rzp_method in ['card', 'upi']:
                payment.payment_method = rzp_method
            else:
                payment.payment_method = 'other'

            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.payment_status = 'completed'
            payment.transaction_id = razorpay_payment_id
            payment.completed_at = timezone.now()
            payment.save()

            booking.status = 'confirmed'
            booking.payment_confirmed_date = timezone.now()
            booking.save()

            # Notifications
            Notification.objects.create(
                user=booking.tenant,
                notification_type='payment_success',
                title='Payment Successful!',
                message=f'Your booking for {booking.pg.title} is confirmed. Check-in from {booking.check_in_date}.',
                booking_id=booking.id,
            )
            Notification.objects.create(
                user=booking.pg.owner,
                notification_type='booking_confirmed',
                title=f'New Confirmed Booking - {booking.tenant.first_name}',
                message=f'{booking.tenant.first_name} completed payment for {booking.pg.title}.',
                booking_id=booking.id,
            )

            messages.success(request, 'Payment successful! Booking confirmed.')
            return redirect('booking_confirmation', booking_id=booking.id)

        else:
            payment.payment_status = 'failed'
            payment.error_message = f"Payment status: {rzp_payment['status']}"
            payment.save()
            messages.error(request, 'Payment not captured. Please try again.')
            return redirect('booking_confirmation', booking_id=booking.id)

    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('booking_confirmation', booking_id=booking.id)


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """Razorpay webhook for async payment events"""
    try:
        webhook_body = request.body.decode('utf-8')
        signature = request.META.get('X-Razorpay-Signature')

        # Verify webhook signature
        try:
            client.utility.verify_webhook_signature(
                webhook_body,
                signature,
                settings.RAZORPAY_WEBHOOK_SECRET
            )
        except razorpay.errors.SignatureVerificationError:
            logger.error("Webhook signature verification failed")
            return HttpResponse(status=400)

        event_data = json.loads(webhook_body)

        if event_data.get('event') == 'payment.captured':
            payment_id = event_data['payload']['payment']['entity']['id']
            payment = Payment.objects.filter(razorpay_payment_id=payment_id).first()

            if payment:
                payment.payment_status = 'completed'
                payment.save()

                booking = payment.booking
                if booking.status != 'confirmed':
                    booking.status = 'confirmed'
                    booking.payment_confirmed_date = timezone.now()
                    booking.save()

                logger.info(f"Webhook confirmed payment: {payment_id}")

        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=500)


@login_required
@require_http_methods(['GET', 'POST'])
def confirm_payment(request, booking_id):
    """Confirm payment either by tenant proof submission or owner manual approval."""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'GET':
        if request.user != booking.tenant:
            messages.error(request, 'Unauthorized.')
            return redirect('home')
        return render(request, 'pgs/confirm_payment.html', {'booking': booking})

    # POST
    if request.user == booking.tenant:
        payment_reference = request.POST.get('payment_reference', '').strip()
        payment_screenshot = request.FILES.get('payment_screenshot')

        if not payment_reference:
            messages.error(request, 'Please provide a payment reference.')
            return redirect('confirm_payment', booking_id=booking_id)

        if booking.status not in ['pending', 'pending_payment_review']:
            messages.info(request, 'This booking cannot be updated at this stage.')
            return redirect('booking_confirmation', booking_id=booking_id)

        booking.payment_reference = payment_reference
        booking.status = 'pending_payment_review'
        if payment_screenshot:
            booking.payment_screenshot = payment_screenshot
        booking.save(update_fields=['payment_reference', 'status', 'payment_screenshot'])
        messages.success(request, 'Payment proof submitted and is awaiting review.')
        return redirect('booking_confirmation', booking_id=booking_id)

    if request.user == booking.pg.owner or request.user.is_staff:
        payment = getattr(booking, 'payment', None)
        if payment:
            payment.payment_status = 'completed'
            payment.save()

        booking.status = 'confirmed'
        booking.payment_confirmed_date = timezone.now()
        booking.save(update_fields=['status', 'payment_confirmed_date'])

        messages.success(request, 'Payment confirmed.')
        return redirect('booking_confirmation', booking_id=booking_id)

    messages.error(request, 'Unauthorized.')
    return redirect('home')


@login_required
@require_POST
def cancel_payment(request, booking_id):
    """Cancel booking and refund if possible"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    
    payment = booking.payment
    if payment:
        payment.payment_status = 'cancelled'
        payment.save()

    booking.status = 'cancelled'
    booking.save()

    messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings_list')
