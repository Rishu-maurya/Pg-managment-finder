from django.urls import path
from . import views

urlpatterns = [
  path('login/', views.user_login, name='user_login'),
  path('signup/', views.signup, name='signup'),
  path('client/register/', views.client_register, name='client_register'),
  path('owner/register/', views.owner_register, name='owner_register'),
  path('activate/<uidb64>/<token>/',views.activate,name='activate'),
  path('logout/', views.user_logout, name='user_logout'),
  path('forgot-password/', views.forgotPassword, name='forgotPassword'),
  path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,     name='resetpassword_validate'),
  path('resetPassword/',views.resetPassword,name='resetPassword'),


  path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
  path('my-profile/', views.my_profile, name='my_profile'),
  path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
  path('my-bookings/', views.my_bookings, name='my_bookings'),
  path('settings/', views.settings_view, name='settings'),
  path('help-support/', views.help_support, name='help_support'),
]
