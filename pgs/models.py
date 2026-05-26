from django.db import models
from users.models import MyUser as Users


class PgListing(models.Model):
    TYPE_CHOICES = [
        ("boys", "Boys"),
        ("girls", "Girls"),
        ("coed", "Coed"),
        ("family", "Family"),
    ]
    SHARING_CHOICES = [
        ("single", "Single"),
        ("double", "Double"),
        ("triple", "Triple"),
        ("quad", "Quad"),
    ]
    FURNISHING_CHOICES = [
        ("fully_furnished", "Fully Furnished"),
        ("semi_furnished", "Semi Furnished"),
        ("unfurnished", "Unfurnished"),
    ]

    owner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="pg_listings")
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude coordinate")
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_from = models.DateField()
    is_available = models.BooleanField(default=True)
    type_of_pg = models.CharField(max_length=20, blank=True, null=True, choices=TYPE_CHOICES)
    amenities = models.TextField(help_text="Comma-separated list of amenities", blank=True, null=True)
    preferred_tenants = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated preferred tenant types",
    )
    furnishing_status = models.CharField(
        max_length=30,
        choices=FURNISHING_CHOICES,
        default="fully_furnished",
    )
    food_available = models.BooleanField(default=False)
    parking_available = models.BooleanField(default=False)
    wifi_available = models.BooleanField(default=False)
    rules_or_restrictions = models.TextField(blank=True)
    sharing_type = models.CharField(max_length=20, choices=SHARING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def amenities_list(self):
        return [item.strip() for item in (self.amenities or "").split(",") if item.strip()]

    def preferred_tenants_list(self):
        return [item.strip() for item in (self.preferred_tenants or "").split(",") if item.strip()]


class PGImage(models.Model):
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="images")
    pg_image = models.ImageField(upload_to="pg_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.pg.title}"


class SavedPg(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="saved_pgs")
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "pg")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.pg.title}"


class VisitRequest(models.Model):
    STATUS_CHOICES = [
        ("visit_requested", "Visit Requested"),
        ("visit_confirmed", "Visit Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="visit_requests")
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="visit_requests")
    preferred_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="visit_requested")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Visit request by {self.user.username} for {self.pg.title}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("pending_payment_review", "Pending Payment Review"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    tenant = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="bookings")
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="bookings")
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    phonepe_upi = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_screenshot = models.ImageField(upload_to="payment_screenshots/", blank=True, null=True)
    payment_confirmed_date = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_bookings",
    )
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-booking_date"]

    def __str__(self):
        return f"Booking by {self.tenant.username} for {self.pg.title}"


class Rating(models.Model):
    """
    Star Rating Model for PG Listings (1-5 stars)
    """
    RATING_CHOICES = [
        (1, "⭐ Poor"),
        (2, "⭐⭐ Fair"),
        (3, "⭐⭐⭐ Good"),
        (4, "⭐⭐⭐⭐ Very Good"),
        (5, "⭐⭐⭐⭐⭐ Excellent"),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="given_ratings")
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "pg")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} rated {self.pg.title} - {self.rating}⭐"

    def get_rating_display_name(self):
        """Return the display name for the rating"""
        return dict(self.RATING_CHOICES).get(self.rating, "Unknown")


class Review(models.Model):
    """
    Review Model for PG Listings with star rating
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="given_reviews")
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="reviews")
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name="review")
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "pg")

    def __str__(self):
        return f"Review by {self.user.username} for {self.pg.title}"


class Payment(models.Model):
    """
    Payment Model for Direct UPI Payment
    Tracks all payment transactions for bookings
    """
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Payment Pending"),
        ("pending_verification", "Pending Verification"),
        ("completed", "Payment Completed"),
        ("failed", "Payment Failed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("upi", "UPI"),
        ("card", "Card"),
        ("other", "Other"),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="upi"
    )

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment for {self.booking} - {self.payment_status}"

    def is_paid(self):
        return self.payment_status == "completed"
