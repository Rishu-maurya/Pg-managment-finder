from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from contact.models import ContactMessage
from pgs.models import Booking, PgListing, SavedPg, VisitRequest
from users.models import MyUser


class PgFeatureTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = MyUser(
            email="owner@example.com",
            username="owner",
            first_name="Owner",
            last_name="User",
            date_of_birth="1990-01-01",
            phone="9000000001",
            is_owner=True,
            is_active=True,
        )
        self.owner.set_password("testpass123")
        self.owner.save()

        self.tenant = MyUser(
            email="tenant@example.com",
            username="tenant",
            first_name="Tenant",
            last_name="User",
            date_of_birth="1995-01-01",
            phone="9000000002",
            is_active=True,
        )
        self.tenant.set_password("testpass123")
        self.tenant.save()

        self.pg = PgListing.objects.create(
            owner=self.owner,
            title="Blue Nest PG",
            slug="blue-nest-pg",
            description="Bright rooms with meals and wifi included.",
            address="123 Market Road",
            city="Delhi",
            state="Delhi",
            pin_code="110001",
            price_per_month="8500.00",
            security_deposit="5000.00",
            available_from=timezone.localdate() + timedelta(days=2),
            is_available=True,
            type_of_pg="coed",
            amenities="Wi-Fi, AC, Laundry",
            preferred_tenants="Students, Working Professionals",
            furnishing_status="fully_furnished",
            food_available=True,
            parking_available=False,
            wifi_available=True,
            rules_or_restrictions="No loud music after 10 PM",
            sharing_type="single",
        )
        self.other_pg = PgListing.objects.create(
            owner=self.owner,
            title="Budget Stay",
            slug="budget-stay",
            description="Budget rooms.",
            address="45 Lake View",
            city="Noida",
            state="UP",
            pin_code="201301",
            price_per_month="4500.00",
            security_deposit="0.00",
            available_from=timezone.localdate() + timedelta(days=5),
            is_available=False,
            type_of_pg="boys",
            amenities="Bed",
            preferred_tenants="Students",
            furnishing_status="semi_furnished",
            food_available=False,
            parking_available=True,
            wifi_available=False,
            sharing_type="double",
        )

    def login_tenant(self):
        self.client.force_login(self.tenant)

    def test_search_filters_and_persists_selected_values(self):
        response = self.client.get(
            reverse("search"),
            {
                "city": "Delhi",
                "sharing_type": "single",
                "type_of_pg": "coed",
                "is_available": "true",
                "sort": "price_low_to_high",
            },
        )
        self.assertEqual(response.status_code, 200)
        pgs = list(response.context["pgs"])
        self.assertEqual(pgs, [self.pg])
        self.assertEqual(response.context["filters"]["city"], "Delhi")
        self.assertEqual(response.context["filters"]["sharing_type"], "single")

    def test_unavailable_pg_cannot_be_booked(self):
        self.login_tenant()
        response = self.client.post(
            reverse("book_pg", kwargs={"pg_slug": self.other_pg.slug}),
            {"check_in_date": (timezone.localdate() + timedelta(days=7)).isoformat()},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Booking.objects.filter(pg=self.other_pg, tenant=self.tenant).exists())

    def test_duplicate_active_booking_is_rejected(self):
        self.login_tenant()
        Booking.objects.create(
            tenant=self.tenant,
            pg=self.pg,
            check_in_date=timezone.localdate() + timedelta(days=2),
            amount="8500.00",
            status="pending",
        )
        self.client.post(
            reverse("book_pg", kwargs={"pg_slug": self.pg.slug}),
            {"check_in_date": (timezone.localdate() + timedelta(days=3)).isoformat()},
            follow=True,
        )
        self.assertEqual(Booking.objects.filter(pg=self.pg, tenant=self.tenant).count(), 1)

    def test_visit_request_creation_does_not_create_booking(self):
        self.login_tenant()
        response = self.client.post(
            reverse("request_visit", kwargs={"pg_slug": self.pg.slug}),
            {
                "preferred_date": (timezone.localdate() + timedelta(days=4)).isoformat(),
                "notes": "Would like an evening visit.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(VisitRequest.objects.filter(pg=self.pg, user=self.tenant).count(), 1)
        self.assertEqual(Booking.objects.filter(pg=self.pg, tenant=self.tenant).count(), 0)

    def test_payment_confirmation_requires_reference(self):
        self.login_tenant()
        booking = Booking.objects.create(
            tenant=self.tenant,
            pg=self.pg,
            check_in_date=timezone.localdate() + timedelta(days=2),
            amount="8500.00",
            status="pending",
        )
        response = self.client.post(reverse("confirm_payment", kwargs={"booking_id": booking.id}), {}, follow=True)
        booking.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(booking.status, "pending")

    def test_submitting_payment_reference_moves_booking_to_review(self):
        self.login_tenant()
        booking = Booking.objects.create(
            tenant=self.tenant,
            pg=self.pg,
            check_in_date=timezone.localdate() + timedelta(days=2),
            amount="8500.00",
            status="pending",
        )
        self.client.post(
            reverse("confirm_payment", kwargs={"booking_id": booking.id}),
            {"payment_reference": "TXN12345"},
            follow=True,
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, "pending_payment_review")
        self.assertEqual(booking.payment_reference, "TXN12345")

    def test_saved_pg_is_unique_and_visible(self):
        self.login_tenant()
        save_url = reverse("toggle_saved_pg", kwargs={"pg_slug": self.pg.slug})
        self.client.post(save_url, {"next": reverse("saved_pg_list")}, follow=True)
        self.client.post(save_url, {"next": reverse("pg_detail", kwargs={"pg_slug": self.pg.slug})}, follow=True)
        self.client.post(save_url, {"next": reverse("saved_pg_list")}, follow=True)
        self.assertEqual(SavedPg.objects.filter(user=self.tenant, pg=self.pg).count(), 1)
        response = self.client.get(reverse("saved_pg_list"))
        self.assertContains(response, "Blue Nest PG")

    def test_listing_detail_uses_real_model_values(self):
        self.login_tenant()
        response = self.client.get(reverse("pg_detail", kwargs={"pg_slug": self.pg.slug}))
        self.assertContains(response, "5000.00")
        self.assertContains(response, "Students, Working Professionals")
        self.assertContains(response, "No loud music after 10 PM")
        self.assertContains(response, self.owner.phone)

    def test_contact_submission_persists_message(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Need help",
                "message": "Please help me with a booking.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)
