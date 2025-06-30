from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class OptimizedUserCreationForm(UserCreationForm):
    """Optimized user registration form with Bootstrap styling"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
        # Update help text for better UX
        self.fields['username'].help_text = 'Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password should be at least 6 characters long.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class OptimizedAuthenticationForm(AuthenticationForm):
    """Optimized login form with Bootstrap styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })


class QuickLoginForm(forms.Form):
    """Quick login form for testing purposes"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
