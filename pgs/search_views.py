"""
Advanced Search & Filter Views with Google Maps Integration
Handles PG listing search, filtering, and map display
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import PgListing, Review, Rating
from .forms import SearchFilterForm


@require_http_methods(['GET'])
def advanced_search(request):
    """
    Advanced search with filtering and sorting
    Supports list view, grid view, and map view
    """
    form = SearchFilterForm(request.GET or None)
    listings = PgListing.objects.filter(is_available=True).select_related('owner').prefetch_related('images', 'ratings')

    # Apply filters
    if form.is_valid():
        # Search query
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            listings = listings.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(city__icontains=search_query)
            )

        # Price range
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        if min_price:
            listings = listings.filter(price_per_month__gte=min_price)
        if max_price:
            listings = listings.filter(price_per_month__lte=max_price)

        # Location
        city = form.cleaned_data.get('city')
        if city:
            listings = listings.filter(city__icontains=city)
        state = form.cleaned_data.get('state')
        if state:
            listings = listings.filter(state__icontains=state)

        # Sharing type
        sharing_type = form.cleaned_data.get('sharing_type')
        if sharing_type:
            listings = listings.filter(sharing_type__in=sharing_type)

        # Type of PG
        type_of_pg = form.cleaned_data.get('type_of_pg')
        if type_of_pg:
            listings = listings.filter(type_of_pg__in=type_of_pg)

        # Furnishing
        furnishing_status = form.cleaned_data.get('furnishing_status')
        if furnishing_status:
            listings = listings.filter(furnishing_status__in=furnishing_status)

        # Amenities
        if form.cleaned_data.get('food_available'):
            listings = listings.filter(food_available=True)
        if form.cleaned_data.get('parking_available'):
            listings = listings.filter(parking_available=True)
        if form.cleaned_data.get('wifi_available'):
            listings = listings.filter(wifi_available=True)

        # Sorting
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            listings = listings.order_by(sort_by)
        else:
            listings = listings.order_by('-created_at')
    else:
        listings = listings.order_by('-created_at')

    # Get view type (list, grid, or map)
    view_type = request.GET.get('view_type', 'list')

    # Add average rating to each listing
    for listing in listings:
        rating_avg = listing.ratings.aggregate(Avg('rating'))['rating__avg']
        listing.average_rating = round(rating_avg, 1) if rating_avg else 0
        listing.rating_count = listing.ratings.count()

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 12 if view_type == 'grid' else 20
    start = (int(page) - 1) * per_page
    end = start + per_page

    paginated_listings = listings[start:end]
    total_count = listings.count()
    total_pages = (total_count + per_page - 1) // per_page

    context = {
        'form': form,
        'listings': paginated_listings,
        'view_type': view_type,
        'total_count': total_count,
        'current_page': int(page),
        'total_pages': total_pages,
        'google_maps_key': settings.GOOGLE_MAPS_EMBED_API_KEY,
    }

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return listings_to_json(paginated_listings)

    return render(request, 'pgs/search/advanced_search.html', context)


def listings_to_json(listings):
    """
    Convert listings to JSON format
    Used for AJAX requests and map markers
    """
    data = []
    for listing in listings:
        rating_avg = listing.ratings.aggregate(Avg('rating'))['rating__avg']
        data.append({
            'id': listing.id,
            'slug': listing.slug,
            'title': listing.title,
            'price': str(listing.price_per_month),
            'city': listing.city,
            'state': listing.state,
            'address': listing.address,
            'latitude': listing.latitude if hasattr(listing, 'latitude') else None,
            'longitude': listing.longitude if hasattr(listing, 'longitude') else None,
            'image_url': listing.images.first().pg_image.url if listing.images.exists() else '/static/images/placeholder.png',
            'rating': round(rating_avg, 1) if rating_avg else 0,
            'room_count': listing.sharing_type if listing.sharing_type else 'N/A',
            'amenities': listing.amenities_list()[:3],
        })
    return JsonResponse({'listings': data})


@require_http_methods(['GET'])
def map_view(request):
    """
    Map view for PG listings with Google Maps
    Shows all listings on an interactive map
    """
    listings = PgListing.objects.filter(is_available=True).select_related('owner').prefetch_related('images')

    # Apply filters (same as search)
    form = SearchFilterForm(request.GET or None)
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            listings = listings.filter(
                Q(title__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(city__icontains=search_query)
            )

        min_price = form.cleaned_data.get('min_price')
        if min_price:
            listings = listings.filter(price_per_month__gte=min_price)
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            listings = listings.filter(price_per_month__lte=max_price)

        city = form.cleaned_data.get('city')
        if city:
            listings = listings.filter(city__icontains=city)

    # Convert to GeoJSON format for map
    features = []
    for listing in listings:
        lat = listing.latitude
        lng = listing.longitude
        has_coordinates = lat is not None and lng is not None

        if not has_coordinates:
            continue
        
        feature = {
            'type': 'Feature',
            'id': listing.id,
            'properties': {
                'title': listing.title,
                'price': f'₹{listing.price_per_month}/month',
                'address': listing.address,
                'city': listing.city,
                'state': listing.state,
                'slug': listing.slug,
                'owner': listing.owner.first_name,
                'image_url': listing.images.first().pg_image.url if listing.images.exists() else '/static/images/placeholder.png',
                'has_coordinates': has_coordinates,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [lng or 0, lat or 0],  # [lng, lat] format for GeoJSON
            }
        }
        features.append(feature)

    context = {
        'form': form,
        'google_maps_key': settings.GOOGLE_MAPS_EMBED_API_KEY,
        'listings_json': json.dumps(features),
        'listings_count': listings.count(),
    }

    return render(request, 'pgs/search/map_view.html', context)


@require_http_methods(['GET'])
def get_map_markers(request):
    """
    API endpoint to get map markers for listings
    Returns GeoJSON FeatureCollection
    """
    listings = PgListing.objects.filter(is_available=True).select_related('owner').prefetch_related('images')

    # Apply filters
    search_query = request.GET.get('q', '').strip()
    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query)
        )

    min_price = request.GET.get('min_price')
    if min_price:
        listings = listings.filter(price_per_month__gte=float(min_price))

    max_price = request.GET.get('max_price')
    if max_price:
        listings = listings.filter(price_per_month__lte=float(max_price))

    city = request.GET.get('city', '').strip()
    if city:
        listings = listings.filter(city__icontains=city)

    # Build GeoJSON
    features = []
    for listing in listings:
        lat = listing.latitude
        lng = listing.longitude

        # Skip if no coordinates are available
        if not lat or not lng:
            continue

        feature = {
            'type': 'Feature',
            'id': listing.id,
            'properties': {
                'title': listing.title,
                'price': f'₹{listing.price_per_month}',
                'address': listing.address,
                'city': listing.city,
                'slug': listing.slug,
                'image_url': listing.images.first().pg_image.url if listing.images.exists() else None,
                'has_coordinates': listing.latitude is not None and listing.longitude is not None,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [float(lng), float(lat)],  # GeoJSON uses [lng, lat]
            }
        }
        features.append(feature)

    return JsonResponse({
        'type': 'FeatureCollection',
        'features': features,
        'count': listings.count(),
    })


@require_http_methods(['GET'])
def quick_search(request):
    """
    Quick search/autocomplete for PG listings
    Returns matching listings as JSON
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    listings = PgListing.objects.filter(
        Q(title__icontains=query) |
        Q(city__icontains=query) |
        Q(address__icontains=query),
        is_available=True
    )[:10]

    results = [{
        'id': listing.id,
        'title': listing.title,
        'city': listing.city,
        'price': f'₹{listing.price_per_month}',
        'slug': listing.slug,
    } for listing in listings]

    return JsonResponse({'results': results})
