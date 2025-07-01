from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Super-fast authentication views
    path('login/', views.fast_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),

    # Password reset views
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('speed-test/', views.login_speed_test, name='login_speed_test'),

    # Alternative fast views
    path('fast-login/', views.fast_login, name='fast_login'),
    path('fast-register/', views.register, name='fast_register'),

    # AJAX endpoints
    path('ajax-login/', views.ajax_login, name='ajax_login'),

    # Fallback to Django's built-in views if needed
    path('django-login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='django_login'),
]
