import math
import json
import urllib.request
from urllib.parse import quote_plus
from django.conf import settings
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .models import Booking, PgListing, SavedPg, VisitRequest, Payment


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _active_compare_ids(request):
    ids = []
    for raw_id in request.GET.getlist("compare"):
        try:
            ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue
    return ids[:3]

def _geocode_address(address):
    """Try to get coordinates from address using Google Geocoding API"""
    api_key = getattr(settings, 'GOOGLE_MAPS_EMBED_API_KEY', None)
    if not api_key or not address:
        return None, None
    address = " ".join(address.split()) # Remove extra whitespace/newlines
    try:
        encoded_address = quote_plus(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data['status'] == 'OK':
                loc = data['results'][0]['geometry']['location']
                return loc['lat'], loc['lng']
    except Exception:
        pass
    return None, None

def _filter_pgs(request, queryset=None):
    if queryset is None:
        queryset = PgListing.objects.all()
    queryset = queryset.filter(owner__is_owner=True).prefetch_related("images", "owner")
    keyword = request.GET.get("keyword", "").strip()
    city = request.GET.get("city", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sharing_type = request.GET.get("sharing_type", "").strip()
    type_of_pg = request.GET.get("type_of_pg", "").strip()
    is_available = request.GET.get("is_available", "").strip()
    sort = request.GET.get("sort", "").strip() or "newest"

    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword)
            | Q(city__icontains=keyword)
            | Q(state__icontains=keyword)
            | Q(address__icontains=keyword)
            | Q(amenities__icontains=keyword)
        )
    if city:
        queryset = queryset.filter(city__iexact=city)
    if min_price:
        queryset = queryset.filter(price_per_month__gte=min_price)
    if max_price:
        queryset = queryset.filter(price_per_month__lte=max_price)
    if sharing_type:
        queryset = queryset.filter(sharing_type=sharing_type)
    if type_of_pg:
        queryset = queryset.filter(type_of_pg=type_of_pg)
    if is_available in {"true", "false"}:
        queryset = queryset.filter(is_available=(is_available == "true"))

    if sort == "price_low_to_high":
        queryset = queryset.order_by("price_per_month", "-created_at")
    elif sort == "available_from":
        queryset = queryset.order_by("available_from", "-created_at")
    else:
        queryset = queryset.order_by("-created_at")

    active_filters = []
    filter_map = {
        "keyword": keyword,
        "city": city,
        "min_price": min_price,
        "max_price": max_price,
        "sharing_type": sharing_type,
        "type_of_pg": type_of_pg,
        "is_available": "Available only" if is_available == "true" else "",
    }
    for key, value in filter_map.items():
        if value:
            active_filters.append({"key": key, "label": f"{key.replace('_', ' ').title()}: {value}"})

    return queryset, {
        "keyword": keyword,
        "city": city,
        "min_price": min_price,
        "max_price": max_price,
        "sharing_type": sharing_type,
        "type_of_pg": type_of_pg,
        "is_available": is_available,
        "sort": sort,
        "active_filters": active_filters,
    }


def _listing_meta(request, listings):
    compare_ids = _active_compare_ids(request)
    compare_pgs = list(PgListing.objects.filter(id__in=compare_ids).prefetch_related("images"))
    saved_pg_ids = set()
    recent_pgs = []
    if request.user.is_authenticated:
        saved_pg_ids = set(
            SavedPg.objects.filter(user=request.user, pg__in=listings).values_list("pg_id", flat=True)
        )
    recent_ids = request.session.get("recent_pg_ids", [])
    if recent_ids:
        preserved_order = Case(*[When(id=pg_id, then=Value(idx)) for idx, pg_id in enumerate(recent_ids)], output_field=IntegerField())
        recent_pgs = list(PgListing.objects.filter(id__in=recent_ids).order_by(preserved_order)[:4])

    cities = PgListing.objects.filter(owner__is_owner=True).order_by("city").values_list("city", flat=True).distinct()
    return {
        "saved_pg_ids": saved_pg_ids,
        "compare_ids": compare_ids,
        "compare_pgs": compare_pgs,
        "recent_pgs": recent_pgs,
        "available_cities": [city for city in cities if city],
        "sharing_choices": PgListing.SHARING_CHOICES,
        "type_choices": PgListing.TYPE_CHOICES,
        "sort_choices": [
            ("newest", "Newest"),
            ("price_low_to_high", "Price: Low to High"),
            ("available_from", "Available From"),
        ],
    }



@login_required(login_url="user_login")
def pg_detail(request, pg_slug):
    try:
        pg = PgListing.objects.prefetch_related("images", "owner").get(slug=pg_slug)
    except PgListing.DoesNotExist as exc:
        raise Http404("PG not found") from exc

    recent_ids = request.session.get("recent_pg_ids", [])
    recent_ids = [pg.id] + [pg_id for pg_id in recent_ids if pg_id != pg.id]
    request.session["recent_pg_ids"] = recent_ids[:6]

    # Owner role check - redirect to dashboard for own PG management
    if request.user.is_authenticated and request.user.is_owner and request.user == pg.owner:
        return redirect(f"{reverse('owner_dashboard')}?pg={pg.slug}")

    off_percent = 37
    price_raw = getattr(pg, "price_per_month", 0) or 0
    try:
        price_dec = Decimal(str(price_raw))
        mrp_dec = price_dec / (Decimal(1) - (Decimal(off_percent) / Decimal(100)))
        mrp = int(math.ceil(mrp_dec))
    except (InvalidOperation, TypeError, ZeroDivisionError):
        mrp = int(price_raw or 0)
        price_dec = Decimal(str(mrp))

    saved = request.user.is_authenticated and SavedPg.objects.filter(user=request.user, pg=pg).exists()
    existing_visit_request = None
    if request.user.is_authenticated:
        existing_visit_request = VisitRequest.objects.filter(
            user=request.user,
            pg=pg,
            status__in=["visit_requested", "visit_confirmed"],
        ).first()

    # Map logic for display
    maps_key = getattr(settings, 'GOOGLE_MAPS_EMBED_API_KEY', '')
    if pg.latitude and pg.longitude:
        map_query = f"{pg.latitude},{pg.longitude}"
    else:
        map_query = f"{pg.address}, {pg.city}, {pg.state} {pg.pin_code}"
    
    encoded_query = quote_plus(map_query)
    if maps_key:
        google_maps_url = f"https://www.google.com/maps/embed/v1/place?key={maps_key}&q={encoded_query}"
    else:
        google_maps_url = f"https://maps.google.com/maps?q={encoded_query}&t=&z=13&ie=UTF8&iwloc=&output=embed"

    context = {
        "pg": pg,
        "mrp": mrp,
        "off": off_percent,
        "show_mrp": mrp > int(price_dec),
        "saved": saved,
        "existing_visit_request": existing_visit_request,
        "today": timezone.localdate().isoformat(),
        "latitude": pg.latitude,
        "longitude": pg.longitude,
        "google_maps_url": google_maps_url,
        "user_role": "owner" if request.user.is_authenticated and request.user.is_owner else "client"
    }
    return render(request, "pgs/pg-specification.html", context)


@login_required(login_url="user_login")
def book_pg(request, pg_slug):
    pg = get_object_or_404(PgListing, slug=pg_slug)
    
    # GET request: Display booking form
    if request.method == "GET":
        if not pg.is_available:
            messages.error(request, "This PG is currently unavailable for booking.")
            return redirect("pg_detail", pg_slug=pg_slug)
        
        context = {
            "pg": pg,
            "today": timezone.localdate().isoformat(),
        }
        return render(request, "pgs/book_form.html", context)
    
    # POST request: Process booking
    if request.method != "POST":
        return redirect("pg_detail", pg_slug=pg_slug)

    if not pg.is_available:
        messages.error(request, "This PG is currently unavailable for booking.")
        return redirect("pg_detail", pg_slug=pg_slug)

    check_in_date = _parse_date(request.POST.get("check_in_date"))
    if not check_in_date:
        messages.error(request, "Please provide a valid check-in date.")
        return redirect("book_pg", pg_slug=pg_slug)
    
    if check_in_date < timezone.localdate():
        messages.error(request, "Check-in date cannot be in the past.")
        return redirect("book_pg", pg_slug=pg_slug)

    # Check for existing active bookings
    existing_booking = Booking.objects.filter(
        tenant=request.user,
        pg=pg,
        status__in=["pending", "pending_payment_review", "confirmed"],
    ).first()
    
    if existing_booking:
        if existing_booking.status == 'pending':
            messages.info(request, "You have an unpaid booking. Please complete the payment.")
            return redirect("initiate_payment", booking_id=existing_booking.id)
        messages.error(request, "You already have an active booking for this PG.")
        return redirect("pg_detail", pg_slug=pg_slug)

    booking = Booking.objects.create(
        tenant=request.user,
        pg=pg,
        check_in_date=check_in_date,
        amount=pg.price_per_month,
        status="pending",
    )
    
    messages.success(request, "Booking created successfully.")
    return redirect("initiate_payment", booking_id=booking.id)
    


@login_required(login_url="user_login")
def request_visit(request, pg_slug):
    pg = get_object_or_404(PgListing, slug=pg_slug)
    if request.method != "POST":
        return redirect("pg_detail", pg_slug=pg_slug)

    preferred_date = _parse_date(request.POST.get("preferred_date"))
    notes = request.POST.get("notes", "").strip()
    if not preferred_date or preferred_date < timezone.localdate():
        messages.error(request, "Please choose a valid future visit date.")
        return redirect("pg_detail", pg_slug=pg_slug)

    visit_request, created = VisitRequest.objects.get_or_create(
        user=request.user,
        pg=pg,
        status="visit_requested",
        defaults={"preferred_date": preferred_date, "notes": notes},
    )
    if created:
        messages.success(request, "Visit request submitted successfully.")
    else:
        visit_request.preferred_date = preferred_date
        visit_request.notes = notes
        visit_request.save(update_fields=["preferred_date", "notes"])
        messages.info(request, "Your existing visit request was updated.")
    return redirect("pg_detail", pg_slug=pg_slug)


@login_required(login_url="user_login")
def toggle_saved_pg(request, pg_slug):
    pg = get_object_or_404(PgListing, slug=pg_slug)
    if request.method != "POST":
        return redirect("pg_detail", pg_slug=pg_slug)

    saved_pg = SavedPg.objects.filter(user=request.user, pg=pg).first()
    if saved_pg:
        saved_pg.delete()
        messages.info(request, "PG removed from your saved list.")
    else:
        SavedPg.objects.create(user=request.user, pg=pg)
        messages.success(request, "PG added to your saved list.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("pg_detail", pg_slug=pg.slug)


@login_required(login_url="user_login")
def saved_pg_list(request):
    saved_items = SavedPg.objects.filter(user=request.user).select_related("pg", "pg__owner").prefetch_related("pg__images")
    return render(request, "pgs/saved_pgs.html", {"saved_items": saved_items})


@login_required(login_url="user_login")
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related("pg", "tenant"), id=booking_id, tenant=request.user)
    timeline = [
        {"key": "pending", "label": "Booking Created"},
        {"key": "pending_payment_review", "label": "Payment Processing"},
        {"key": "confirmed", "label": "Booking Confirmed"},
        {"key": "completed", "label": "Completed"},
    ]
    current_index = next(
        (index for index, item in enumerate(timeline) if item["key"] == booking.status),
        0,
    )
    for index, item in enumerate(timeline):
        item["done"] = index <= current_index

    context = {
        "booking": booking,
        "pg": booking.pg,
        "timeline": timeline,
    }
    return render(request, "pgs/booking_confirmation.html", context)


@login_required(login_url="user_login")
def my_bookings_list(request):
    bookings = Booking.objects.filter(tenant=request.user).select_related("pg", "pg__owner").order_by("-booking_date")
    visit_requests = VisitRequest.objects.filter(user=request.user).select_related("pg").order_by("-created_at")
    return render(
        request,
        "pgs/my_bookings_list.html",
        {
            "bookings": bookings,
            "visit_requests": visit_requests,
        },
    )


def search(request):
    listings, filters = _filter_pgs(request)
    context = {
        "pgs": listings,
        "filters": filters,
        "search_mode": True,
    }
    context.update(_listing_meta(request, listings))
    return render(request, "pgs/pgs.html", context)


def pgs(request):
    listings, filters = _filter_pgs(request, PgListing.objects.all())
    context = {
        "pgs": listings,
        "filters": filters,
        "search_mode": False,
    }
    context.update(_listing_meta(request, listings))
    return render(request, "pgs/pgs.html", context)


def about(request):
    return render(request, "about.html")


@login_required(login_url="user_login")
def pg_register(request):
    if not request.user.is_owner:
        return redirect("home")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin_code = request.POST.get("pin_code")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        price_per_month = request.POST.get("price_per_month")
        security_deposit = request.POST.get("security_deposit") or 0
        available_from = request.POST.get("available_from")
        type_of_pg = request.POST.get("type_of_pg")
        amenities = request.POST.get("amenities")
        preferred_tenants = request.POST.get("preferred_tenants")
        furnishing_status = request.POST.get("furnishing_status") or "fully_furnished"
        sharing_type = request.POST.get("sharing_type")
        rules_or_restrictions = request.POST.get("rules_or_restrictions", "")
        pg_images = request.FILES.getlist("pg_images")

        slug = slugify(title)
        base_slug = slug
        counter = 1
        while PgListing.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Sanitize coordinates: handle empty strings or literal "None" from frontend
        if not latitude or str(latitude).strip().lower() in ["", "none"]:
            latitude = None
        if not longitude or str(longitude).strip().lower() in ["", "none"]:
            longitude = None

        # Automatic geocoding if coordinates are missing from frontend
        if latitude is None or longitude is None:
            full_address = f"{address}, {city}, {state}, {pin_code}, India"
            lat_found, lng_found = _geocode_address(full_address)
            latitude = lat_found if lat_found else latitude
            longitude = lng_found if lng_found else longitude

        pg_listing = PgListing.objects.create(
            owner=request.user,
            title=title,
            slug=slug,
            description=description,
            address=address,
            city=city,
            state=state,
            pin_code=pin_code,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None,
            price_per_month=price_per_month,
            security_deposit=security_deposit,
            available_from=available_from,
            type_of_pg=type_of_pg,
            amenities=amenities,
            preferred_tenants=preferred_tenants,
            furnishing_status=furnishing_status,
            food_available=bool(request.POST.get("food_available")),
            parking_available=bool(request.POST.get("parking_available")),
            wifi_available=bool(request.POST.get("wifi_available")),
            rules_or_restrictions=rules_or_restrictions,
            sharing_type=sharing_type,
            is_available=request.POST.get("is_available") == "1",
        )

        for image in pg_images:
            pg_listing.images.create(pg_image=image)

        messages.success(request, "PG listing created successfully.")
        return redirect("pgs")
    return render(request, "users/owners/pgregister.html", {
        'google_maps_key': settings.GOOGLE_MAPS_EMBED_API_KEY,
    })


@login_required(login_url="user_login")
def pg_edit(request, pg_slug):
    pg_listing = get_object_or_404(PgListing, slug=pg_slug, owner=request.user)

    if request.method == "POST":
        title = request.POST.get("title", pg_listing.title)
        address = request.POST.get("address", pg_listing.address)
        city = request.POST.get("city", pg_listing.city)
        state = request.POST.get("state", pg_listing.state)
        pin_code = request.POST.get("pin_code", pg_listing.pin_code)
        pg_listing.description = request.POST.get("description", pg_listing.description)

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Sanitize coordinates: handle empty strings or literal "None" from frontend
        if not latitude or str(latitude).strip().lower() in ["", "none"]:
            latitude = None
        if not longitude or str(longitude).strip().lower() in ["", "none"]:
            longitude = None

        # Re-geocode if address changed or coordinates are missing
        addr_changed = (address != pg_listing.address or city != pg_listing.city or pin_code != pg_listing.pin_code)

        # Update coordinates automatically if missing
        if latitude is None or longitude is None or addr_changed:
            full_address = f"{address}, {city}, {state}, {pin_code}, India"
            lat_found, lng_found = _geocode_address(full_address)
            if lat_found and lng_found:
                latitude = lat_found
                longitude = lng_found

        pg_listing.title = title
        pg_listing.address = address
        pg_listing.city = city
        pg_listing.state = state
        pg_listing.pin_code = pin_code
        pg_listing.latitude = latitude if latitude else pg_listing.latitude
        pg_listing.longitude = longitude if longitude else pg_listing.longitude

        pg_listing.price_per_month = request.POST.get("price_per_month") or pg_listing.price_per_month
        pg_listing.security_deposit = request.POST.get("security_deposit") or pg_listing.security_deposit
        pg_listing.available_from = request.POST.get("available_from") or pg_listing.available_from
        pg_listing.type_of_pg = request.POST.get("type_of_pg") or pg_listing.type_of_pg
        pg_listing.amenities = request.POST.get("amenities")
        pg_listing.preferred_tenants = request.POST.get("preferred_tenants")
        pg_listing.furnishing_status = request.POST.get("furnishing_status") or pg_listing.furnishing_status
        pg_listing.sharing_type = request.POST.get("sharing_type") or pg_listing.sharing_type
        pg_listing.rules_or_restrictions = request.POST.get("rules_or_restrictions", pg_listing.rules_or_restrictions)
        pg_listing.food_available = request.POST.get("food_available") == "1"
        pg_listing.parking_available = request.POST.get("parking_available") == "1"
        pg_listing.wifi_available = request.POST.get("wifi_available") == "1"
        pg_listing.is_available = request.POST.get("is_available") == "1"
        pg_listing.save()

        new_images = request.FILES.getlist("pg_images")
        if new_images:
            pg_listing.images.all().delete()
            for image in new_images:
                pg_listing.images.create(pg_image=image)

        messages.success(request, "PG listing updated successfully.")
        return redirect("owner_dashboard")

    return render(request, "users/owners/pg_edit.html", {"pg": pg_listing})


@login_required(login_url="user_login")
def pg_delete(request, pg_slug):
    pg_listing = get_object_or_404(PgListing, slug=pg_slug, owner=request.user)
    if request.method == "POST":
        pg_listing.delete()
        messages.success(request, "PG listing deleted successfully.")
        return redirect("owner_dashboard")

    return render(request, "users/owners/pg_delete_confirm.html", {"pg": pg_listing})


@login_required(login_url="user_login")
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if request.method == "POST":
        if booking.status == "cancelled":
            messages.info(request, "Booking already cancelled.")
        elif booking.status == "completed":
            messages.error(request, "Completed bookings cannot be cancelled.")
        else:
            booking.status = "cancelled"
            booking.save(update_fields=["status", "updated_at"])
            messages.success(request, "Booking cancelled successfully.")
    return redirect("my_bookings_list")


@login_required(login_url="user_login")
def compare_pgs(request):
    compare_ids = _active_compare_ids(request)
    compare_pgs = PgListing.objects.filter(id__in=compare_ids).prefetch_related("images")[:3]
    return render(request, "pgs/compare.html", {"compare_pgs": compare_pgs})


@login_required(login_url="user_login")
def owner_booking_reviews(request):
    if not (request.user.is_owner or request.user.is_staff):
        messages.error(request, "You do not have access to booking reviews.")
        return redirect("home")

    filters = Q(pg__owner=request.user) if request.user.is_owner and not request.user.is_staff else Q()
    bookings = Booking.objects.filter(filters).select_related("tenant", "pg", "reviewed_by")
    visit_requests = VisitRequest.objects.filter(filters).select_related("user", "pg")
    return render(
        request,
        "pgs/owner_booking_reviews.html",
        {"bookings": bookings, "visit_requests": visit_requests},
    )


@login_required(login_url="user_login")
def review_booking(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related("pg"), id=booking_id)
    if not (request.user.is_staff or booking.pg.owner_id == request.user.id):
        messages.error(request, "You do not have access to this booking.")
        return redirect("home")

    if request.method == "POST":
        action = request.POST.get("action")
        booking.review_notes = request.POST.get("review_notes", "").strip()
        booking.reviewed_by = request.user
        if action == "approve":
            booking.status = "confirmed"
            booking.payment_confirmed_date = timezone.now()
            messages.success(request, "Booking marked as confirmed.")
        elif action == "reject":
            booking.status = "pending"
            booking.payment_confirmed_date = None
            messages.info(request, "Booking moved back to pending payment.")
        booking.save()
    return redirect("owner_booking_reviews")


@login_required(login_url="user_login")
def review_visit_request(request, visit_request_id):
    visit_request = get_object_or_404(VisitRequest.objects.select_related("pg"), id=visit_request_id)
    if not (request.user.is_staff or visit_request.pg.owner_id == request.user.id):
        messages.error(request, "You do not have access to this visit request.")
        return redirect("home")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "confirm":
            visit_request.status = "visit_confirmed"
            messages.success(request, "Visit request confirmed.")
        elif action == "cancel":
            visit_request.status = "cancelled"
            messages.info(request, "Visit request cancelled.")
        visit_request.save(update_fields=["status"])
    return redirect("owner_booking_reviews")
