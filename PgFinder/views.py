from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from contact.models import ContactMessage
from pgs.models import Booking, PGImage, PgListing


def home(request):
    pg_listings = PgListing.objects.filter(owner__is_owner=True).prefetch_related("images", "owner")[:8]
    pg_images = PGImage.objects.all()[:8]
    context = {
        "pg_listings": pg_listings,
        "pg_images": pg_images,
        "metrics": {
            "total_listings": PgListing.objects.filter(owner__is_owner=True).count(),
            "available_listings": PgListing.objects.filter(owner__is_owner=True, is_available=True).count(),
            "pending_bookings": Booking.objects.filter(status__in=["pending", "pending_payment_review"]).count(),
            "confirmed_bookings": Booking.objects.filter(status="confirmed").count(),
            "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
        },
        "available_cities": list(
            PgListing.objects.filter(owner__is_owner=True).order_by("city").values_list("city", flat=True).distinct()
        ),
        "sharing_choices": PgListing.SHARING_CHOICES,
        "type_choices": PgListing.TYPE_CHOICES,
    }
    return render(request, "home.html", context)


def about(request):
    info = {
        "title": "About PG Finder",
        "description": (
            "PG Finder (E-Hostel & PG) is a platform to connect clients looking for paying-guest "
            "accommodation with property owners. Our goal is to simplify PG search, listing, and "
            "management by providing an easy-to-use interface, secure user accounts, and built-in "
            "communication tools."
        ),
        "features": [
            "Search PG listings by city, price, amenities, availability, and sharing type",
            "Owners can register and list their PGs with images and specifications",
            "Clients can register, browse listings, save favorites, and request visits",
            "Payment-proof based booking flow with owner/admin review",
            "Secure authentication and profile management",
        ],
        "how_it_works": [
            "Create an account as a client or an owner",
            "Owners add PG listings with details and photos",
            "Clients browse listings, compare shortlisted options, and save favorites",
            "Use the dashboard to manage bookings, visit requests, and support needs",
        ],
        "privacy": (
            "We use your data to provide and improve the service. Sensitive information like "
            "Aadhar is stored only when explicitly provided by owners and should be handled with care. "
            "Do not share credentials or private data publicly."
        ),
        "contact": {
            "email": "support@example.com",
            "note": "For feature requests or support, email us. Do not include passwords in email.",
        },
    }
    return render(request, "about.html", info)


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        try:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text,
            )
        except Exception:
            pass

        if not subject:
            subject = f"Inquiry from {name or email}"

        full_message = f"From: {name} <{email}>\n\n{message_text}"
        recipients = ["harshtheking94@gmail.com", "harshtheking04@gmail.com"]
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")
        sent_ok = False

        try:
            EmailMessage(subject, full_message, from_email=from_email, to=recipients).send()
            sent_ok = True
        except Exception:
            sent_ok = False

        if email:
            try:
                ack_subject = f"We've received your message: {subject}"
                ack_body = (
                    f"Hi {name or ''},\n\n"
                    "Thanks for contacting PG Finder. We've received your inquiry and will reply soon. "
                    "Below is a copy of your message:\n\n"
                    f"{message_text}\n\n"
                    "- PG Finder Team"
                )
                EmailMessage(ack_subject, ack_body, from_email=from_email, to=[email]).send()
            except Exception:
                pass

        if sent_ok:
            messages.success(request, "Thanks, your message has been sent. We will reply soon.")
            return redirect("contact")

        messages.error(request, "Failed to send message to support email. Please try again later.")

    contact_summary = {
        "total_messages": ContactMessage.objects.count(),
        "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
    }
    return render(request, "contact.html", {"contact_summary": contact_summary})
