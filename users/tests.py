from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from pgs.models import Booking, PgListing, VisitRequest
from users.models import MyUser


class OwnerDashboardTests(TestCase):
    def setUp(self):
        self.owner = MyUser(
            email="owner-dashboard@example.com",
            username="ownerdashboard",
            first_name="Owner",
            last_name="Dashboard",
            date_of_birth="1990-01-01",
            phone="9000000101",
            is_owner=True,
            is_active=True,
        )
        self.owner.set_password("testpass123")
        self.owner.save()

        self.tenant = MyUser(
            email="tenant-dashboard@example.com",
            username="tenantdashboard",
            first_name="Tenant",
            last_name="Dashboard",
            date_of_birth="1996-01-01",
            phone="9000000102",
            is_active=True,
        )
        self.tenant.set_password("testpass123")
        self.tenant.save()

        self.pg = PgListing.objects.create(
            owner=self.owner,
            title="Owner Dashboard PG",
            slug="owner-dashboard-pg",
            description="Dashboard listing",
            address="221B Baker Street",
            city="Delhi",
            state="Delhi",
            pin_code="110001",
            price_per_month="9000.00",
            security_deposit="3000.00",
            available_from=timezone.localdate() + timedelta(days=2),
            is_available=True,
            type_of_pg="coed",
            amenities="Wi-Fi, Laundry",
            preferred_tenants="Students",
            furnishing_status="fully_furnished",
            sharing_type="single",
        )
        Booking.objects.create(
            tenant=self.tenant,
            pg=self.pg,
            check_in_date=timezone.localdate() + timedelta(days=7),
            amount="9000.00",
            status="pending_payment_review",
        )
        VisitRequest.objects.create(
            user=self.tenant,
            pg=self.pg,
            preferred_date=timezone.localdate() + timedelta(days=3),
            status="visit_requested",
        )

    def test_owner_dashboard_requires_owner_role(self):
        self.client.force_login(self.tenant)
        response = self.client.get(reverse("owner_dashboard"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owner dashboard is only available")

    def test_owner_dashboard_renders_metrics_and_map_fallback(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("owner_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owner Dashboard")
        self.assertContains(response, "Owner Dashboard PG")
        self.assertContains(response, "maps.google.com")
        self.assertContains(response, "Pending payment reviews")

    @override_settings(GOOGLE_MAPS_EMBED_API_KEY="abc123")
    def test_owner_dashboard_uses_embed_api_when_key_is_configured(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("owner_dashboard"))
        self.assertContains(response, "google.com/maps/embed/v1/place")
        self.assertContains(response, "key=abc123")
