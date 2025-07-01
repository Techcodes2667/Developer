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

                    return redirect('/patients/dashboard/')

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
@csrf_protect
def fast_login(request):
    """Ultra-fast login view with minimal processing"""
    if request.user.is_authenticated:
        return redirect('patients:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if username and password:
            try:
                # Direct database lookup for speed - only get necessary fields
                user = User.objects.only('id', 'username', 'password', 'first_name', 'is_active').get(
                    username=username, is_active=True
                )

                # Quick password check
                if check_password(password, user.password):
                    # Manual login without Django's slow authenticate()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)

                    # Skip messages for speed - just redirect
                    next_page = request.GET.get('next', '/patients/dashboard/')
                    return redirect(next_page)
                else:
                    messages.error(request, 'Invalid credentials.')
            except User.DoesNotExist:
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
