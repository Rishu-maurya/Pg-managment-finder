from django import forms
from .models import PgListing, PGImage, Review, Rating
from django.core.exceptions import ValidationError


class AddPGForm(forms.ModelForm):
    """
    Form for PG Owners to add new PG listings
    """
    # Override amenities and preferred_tenants to use checkboxes instead
    amenities = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amenities separated by commas (e.g., WiFi, AC, Kitchen, Parking)',
            'rows': 3
        }),
        help_text="Comma-separated list of amenities",
        required=False
    )
    preferred_tenants = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter preferred tenants separated by commas',
            'rows': 2
        }),
        help_text="Comma-separated preferred tenant types",
        required=False
    )

    class Meta:
        model = PgListing
        fields = ('title', 'description', 'address', 'city', 'state', 'pin_code',
                  'latitude', 'longitude', 'price_per_month', 'security_deposit', 'available_from', 'type_of_pg',
                  'sharing_type', 'furnishing_status', 'amenities', 'preferred_tenants',
                  'food_available', 'parking_available', 'wifi_available',
                  'rules_or_restrictions', 'is_available')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PG Listing Title (e.g., Modern 2BHK Near Metro)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your PG...',
                'rows': 5
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PIN Code',
                'maxlength': '6'
            }),
            'latitude': forms.HiddenInput(attrs={
                'id': 'id_latitude'
            }),
            'longitude': forms.HiddenInput(attrs={
                'id': 'id_longitude'
            }),
            'price_per_month': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monthly rent (₹)',
                'step': '100'
            }),
            'security_deposit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Security deposit (₹)',
                'step': '100'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'type_of_pg': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sharing_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'furnishing_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rules_or_restrictions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any rules or restrictions...',
                'rows': 3
            }),
            'food_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'parking_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'wifi_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price_per_month')
        deposit = cleaned_data.get('security_deposit')

        if price and price < 0:
            raise ValidationError("Price cannot be negative.")
        if deposit and deposit < 0:
            raise ValidationError("Security deposit cannot be negative.")

        return cleaned_data


class EditPGForm(AddPGForm):
    """
    Form for PG Owners to edit existing PG listings
    Inherits from AddPGForm
    """
    pass


class PGImageForm(forms.ModelForm):
    """
    Form for uploading PG images
    """
    class Meta:
        model = PGImage
        fields = ('pg_image',)
        widgets = {
            'pg_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_pg_image(self):
        image = self.cleaned_data.get('pg_image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image size cannot exceed 5MB.")
        return image


class RatingForm(forms.ModelForm):
    """
    Form for users to rate a PG
    """
    class Meta:
        model = Rating
        fields = ('rating',)
        widgets = {
            'rating': forms.RadioSelect(choices=Rating.RATING_CHOICES, attrs={
                'class': 'form-check-input'
            })
        }


class ReviewForm(forms.ModelForm):
    """
    Form for users to write a review for a PG
    """
    class Meta:
        model = Review
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title (e.g., Great location and friendly management)',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your detailed review...',
                'rows': 5
            })
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content and len(content) < 20:
            raise ValidationError("Review must be at least 20 characters long.")
        return content


class SearchFilterForm(forms.Form):
    """
    Advanced search and filter form for PG listings
    Allows users to search by multiple criteria
    """
    # Search text
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by location, title, or address...',
            'id': 'search_query'
        })
    )

    # Price range
    min_price = forms.DecimalField(
        required=False,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '₹ Min Price',
            'min': '0',
            'step': '1000'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '₹ Max Price',
            'step': '1000'
        })
    )

    # Location
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
            'id': 'city'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State',
            'id': 'state'
        })
    )

    # Sharing type
    sharing_type = forms.MultipleChoiceField(
        required=False,
        choices=PgListing.SHARING_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    # Type of PG
    type_of_pg = forms.MultipleChoiceField(
        required=False,
        choices=PgListing.TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    # Furnishing type
    furnishing_status = forms.MultipleChoiceField(
        required=False,
        choices=PgListing.FURNISHING_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    # Amenities (checkboxes)
    food_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Food Available"
    )
    parking_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Parking Available"
    )
    wifi_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="WiFi Available"
    )

    # Availability
    is_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Currently Available"
    )

    # Sorting
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('price_per_month', 'Price: Low to High'),
        ('-price_per_month', 'Price: High to Low'),
        ('title', 'Title: A to Z'),
        ('-title', 'Title: Z to A'),
    ]
    sort_by = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'sort_by'
        })
    )

    # View type
    VIEW_CHOICES = [
        ('list', 'List View'),
        ('map', 'Map View'),
        ('grid', 'Grid View'),
    ]
    view_type = forms.ChoiceField(
        required=False,
        choices=VIEW_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price and min_price > max_price:
            raise ValidationError("Minimum price cannot be greater than maximum price.")

        return cleaned_data

