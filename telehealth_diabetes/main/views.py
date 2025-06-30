from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def home(request):
    """Home page view"""
    return render(request, 'main/home.html')

def about(request):
    """About page view"""
    return render(request, 'main/about.html')

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Here you would typically send an email or save to database
        messages.success(request, 'Thank you for your message. We will get back to you soon!')
        return redirect('main:contact')

    return render(request, 'main/contact.html')

def privacy(request):
    """Privacy policy page"""
    return render(request, 'main/privacy.html')

def terms(request):
    """Terms of service page"""
    return render(request, 'main/terms.html')

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('main:login')
    else:
        form = UserCreationForm()

    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_page = request.GET.get('next', 'main:home')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main:home')

def community(request):
    """Community page view"""
    return render(request, 'main/community.html')

@require_http_methods(["GET"])
def health_check(request):
    """Health check Endpoint for monitoring"""
    return JsonResponse({'status': 'healthy', 'service': 'telehealth_diabetes'})
