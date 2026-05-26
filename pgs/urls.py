from django.urls import path

from . import views
from .search_views import (
    advanced_search,
    map_view,
    get_map_markers,
    quick_search,
)
from .payment_views import (
    initiate_payment,
    razorpay_verify_payment,
    razorpay_webhook,
    confirm_payment,
    cancel_payment,
)

urlpatterns = [
    path("", views.pgs, name="pgs"),
    path("about/", views.about, name="about"),
    path("search/", views.search, name="search"),
    path("pgregister/", views.pg_register, name="pg_register"),
    path("saved/", views.saved_pg_list, name="saved_pg_list"),
    path("compare/", views.compare_pgs, name="compare_pgs"),
    path("owner/reviews/", views.owner_booking_reviews, name="owner_booking_reviews"),
    path("owner/edit/<slug:pg_slug>/", views.pg_edit, name="pg_edit"),
    path("owner/delete/<slug:pg_slug>/", views.pg_delete, name="pg_delete"),
    path("book/<slug:pg_slug>/", views.book_pg, name="book_pg"),
    path("visit/<slug:pg_slug>/", views.request_visit, name="request_visit"),
    path("save/<slug:pg_slug>/", views.toggle_saved_pg, name="toggle_saved_pg"),
    path("booking-confirmation/<int:booking_id>/", views.booking_confirmation, name="booking_confirmation"),
    path("review-booking/<int:booking_id>/", views.review_booking, name="review_booking"),
    path("review-visit/<int:visit_request_id>/", views.review_visit_request, name="review_visit_request"),
    path("my-bookings/", views.my_bookings_list, name="my_bookings_list"),
    path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),

    # Advanced Search & Filter
    path('advanced-search/', advanced_search, name='advanced_search'),
    path('map/', map_view, name='map_view'),
    path('api/map-markers/', get_map_markers, name='get_map_markers'),
    path('api/quick-search/', quick_search, name='quick_search'),

    # Razorpay Payment URLs
    path('payment/initiate/<int:booking_id>/', initiate_payment, name='initiate_payment'),
    path('payment/razorpay-verify/<int:booking_id>/', razorpay_verify_payment, name='razorpay_verify_payment'),
    path('payment/webhook/', razorpay_webhook, name='razorpay_webhook'),
    path('payment/confirm/<int:booking_id>/', confirm_payment, name='confirm_payment'),
    path('payment/cancel/<int:booking_id>/', cancel_payment, name='cancel_payment'),

    path("<slug:pg_slug>/", views.pg_detail, name="pg_detail"),

]

