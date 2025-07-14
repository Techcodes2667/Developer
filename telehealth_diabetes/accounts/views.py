from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
import time

from .forms import OptimizedUserCreationForm, OptimizedAuthenticationForm

@never_cache
def instant_register(request):
    """INSTANT registration - minimal validation for development speed"""
    if request.user.is_authenticated:
        return redirect('patients:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip() or f"{username}@test.com"

        if username:
            try:
                # Check if user exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username exists.')
                else:
                    # INSTANT user creation - minimal data
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='instant123',  # Default password for speed
                        first_name=username.title(),
                    )

                    # Instant login with standard backend
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)

                    return redirect('patients:dashboard')

            except Exception as e:
                messages.error(request, 'Registration failed.')
        else:
            messages.error(request, 'Username required.')

    return render(request, 'accounts/instant_register.html', {'debug': True})


@never_cache
@csrf_protect
def register(request):
    """Ultra-fast user registration view"""
    if request.user.is_authenticated:
        return redirect('patients:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Ultra-fast validation - minimal checks
        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 3:
            messages.error(request, 'Password too short.')
        else:
            try:
                # Check for existing users with single query
                if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                    messages.error(request, 'Username or email already exists.')
                else:
                    # Create user directly for speed
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password1,
                        first_name=first_name,
                        last_name=last_name
                    )

                    # Quick login without messages
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)

                    return redirect('patients:dashboard')

            except Exception as e:
                messages.error(request, 'Registration failed. Please try again.')

    # Simple form context
    context = {
        'form': {
            'username': request.POST.get('username', '') if request.method == 'POST' else '',
            'email': request.POST.get('email', '') if request.method == 'POST' else '',
            'first_name': request.POST.get('first_name', '') if request.method == 'POST' else '',
            'last_name': request.POST.get('last_name', '') if request.method == 'POST' else '',
        }
    }
    return render(request, 'accounts/fast_register.html', context)

@never_cache
def instant_login(request):
    """INSTANT login - bypasses all validation for development speed"""
    if request.user.is_authenticated:
        return redirect('patients:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()

        if username:
            try:
                # INSTANT LOGIN - no password check in development!
                user = User.objects.get(username=username, is_active=True)

                # Debug logging
                print(f"DEBUG: Found user {user.username}, attempting login...")

                # Use standard Django backend for reliability
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                # Debug logging
                print(f"DEBUG: Login successful, user authenticated: {request.user.is_authenticated}")
                print(f"DEBUG: Redirecting to patients:dashboard")

                # Immediate redirect
                return redirect('patients:dashboard')

            except User.DoesNotExist:
                print(f"DEBUG: User {username} not found")
                messages.error(request, 'User not found.')
            except Exception as e:
                print(f"DEBUG: Login error: {e}")
                messages.error(request, 'Login failed.')
        else:
            messages.error(request, 'Please enter username.')

    return render(request, 'accounts/instant_login.html', {'debug': True})


@never_cache
@csrf_protect
def fast_login(request):
    """Ultra-fast login view with minimal processing"""
    if request.user.is_authenticated:
        return redirect('patients:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if username and password:
            # Use ultra-fast authentication backend
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('patients:dashboard')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Please enter both username and password.')

    # Minimal context for speed
    return render(request, 'accounts/fast_login.html', {'debug': True})

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html')

# AJAX endpoint for quick login testing
@csrf_protect
def ajax_login(request):
    """AJAX login endpoint for faster authentication"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': f'Welcome back, {user.first_name or username}!',
                    'redirect_url': '/patients/dashboard/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid username or password.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@never_cache
@csrf_protect
def forgot_password(request):
    """Password reset request view"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Please enter your email address.')
        else:
            try:
                user = User.objects.get(email=email)

                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Get current site
                current_site = get_current_site(request)

                # Create reset link
                reset_link = f"http://{current_site.domain}/accounts/reset-password/{uid}/{token}/"

                # Email content
                subject = 'Password Reset - Telehealth Diabetes Care'
                message = f"""
Hello {user.first_name or user.username},

You requested a password reset for your Telehealth Diabetes Care account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours for security reasons.

If you didn't request this reset, please ignore this email.

Best regards,
Telehealth Diabetes Care Team
                """

                # Send email
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request,
                        f'Password reset instructions have been sent to {email}. '
                        'Please check your email and follow the instructions.')
                    return redirect('accounts:login')

                except Exception as e:
                    messages.error(request,
                        'Unable to send email. Please try again later or contact support.')
                    print(f"Email error: {e}")  # For debugging

            except User.DoesNotExist:
                # Don't reveal if email exists or not for security
                messages.success(request,
                    f'If an account with email {email} exists, '
                    'password reset instructions have been sent.')
                return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html')

@never_cache
@csrf_protect
def reset_password(request, uidb64, token):
    """Password reset confirmation view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')

            # Basic validation
            if not password1:
                messages.error(request, 'Password is required.')
            elif len(password1) < 6:
                messages.error(request, 'Password must be at least 6 characters long.')
            elif password1 != password2:
                messages.error(request, 'Passwords do not match.')
            else:
                # Set new password
                user.set_password(password1)
                user.save()

                messages.success(request,
                    'Your password has been reset successfully! You can now log in with your new password.')
                return redirect('accounts:login')

        return render(request, 'accounts/reset_password.html', {
            'validlink': True,
            'user': user
        })
    else:
        return render(request, 'accounts/reset_password.html', {
            'validlink': False
        })


def login_speed_test(request):
    """Login speed test page"""
    return render(request, 'accounts/login_speed_test.html')


def performance_dashboard(request):
    """Performance dashboard for testing all authentication methods"""
    return render(request, 'accounts/performance_dashboard.html')


def create_test_users(request):
    """Create test users for development"""
    from patients.models import PatientProfile
    from datetime import date

    # Create demo user
    demo_user, created1 = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@test.com',
            'first_name': 'Demo',
            'last_name': 'User',
            'is_active': True,
        }
    )
    if created1:
        demo_user.set_password('demo123')
        demo_user.save()

    # Create PatientProfile for demo user
    demo_profile, profile_created1 = PatientProfile.objects.get_or_create(
        user=demo_user,
        defaults={
            'diabetes_type': 'type2',
            'date_of_birth': date(1985, 5, 15),
            'gender': 'M',
            'phone_number': '+1234567890',
            'diagnosis_date': date(2020, 3, 10),
            'hba1c_target': 7.0,
            'blood_glucose_target_min': 4.0,
            'blood_glucose_target_max': 10.0,
        }
    )

    # Create test patient
    test_user, created2 = User.objects.get_or_create(
        username='testpatient',
        defaults={
            'email': 'testpatient@test.com',
            'first_name': 'Test',
            'last_name': 'Patient',
            'is_active': True,
        }
    )
    if created2:
        test_user.set_password('testpass123')
        test_user.save()

    # Create PatientProfile for test patient
    test_profile, profile_created2 = PatientProfile.objects.get_or_create(
        user=test_user,
        defaults={
            'diabetes_type': 'type1',
            'date_of_birth': date(1990, 8, 22),
            'gender': 'F',
            'phone_number': '+1987654321',
            'diagnosis_date': date(2018, 6, 5),
            'hba1c_target': 6.5,
            'blood_glucose_target_min': 4.0,
            'blood_glucose_target_max': 8.0,
        }
    )

    # Create admin user
    admin_user, created3 = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created3:
        admin_user.set_password('admin123')
        admin_user.save()

    # Create PatientProfile for admin user (so they can test patient features)
    admin_profile, profile_created3 = PatientProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'diabetes_type': 'type2',
            'date_of_birth': date(1980, 12, 1),
            'gender': 'O',
            'phone_number': '+1555000000',
            'diagnosis_date': date(2019, 1, 15),
            'hba1c_target': 7.5,
            'blood_glucose_target_min': 4.5,
            'blood_glucose_target_max': 9.0,
        }
    )

    users_created = sum([created1, created2, created3])
    profiles_created = sum([profile_created1, profile_created2, profile_created3])
    total_users = User.objects.count()

    return render(request, 'accounts/test_users_created.html', {
        'users_created': users_created,
        'profiles_created': profiles_created,
        'total_users': total_users,
        'demo_user': demo_user,
        'test_user': test_user,
        'admin_user': admin_user,
    })
