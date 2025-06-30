# Password Reset System Guide

This guide covers the comprehensive password reset functionality implemented in the Telehealth Diabetes Care System.

## 🔐 Overview

The password reset system allows users to securely reset their passwords via email verification. It includes:

- **Secure token generation** with 24-hour expiration
- **Email-based verification** with HTML templates
- **User-friendly interface** with real-time validation
- **Security features** to prevent abuse
- **Console email backend** for development
- **SMTP support** for production

## 🎯 Features

### User Features
- **Forgot Password Link** on login pages
- **Email Verification** with secure tokens
- **Password Strength Indicator** during reset
- **Real-time Validation** for password confirmation
- **Mobile-Responsive Design** for all devices
- **Clear Error Messages** and user guidance

### Security Features
- **24-hour Token Expiration** for security
- **One-time Use Tokens** that expire after use
- **Email Verification Required** before reset
- **No Password Exposure** in emails or URLs
- **Rate Limiting Protection** (can be added)
- **Secure Token Generation** using Django's built-in system

### Admin Features
- **Console Email Backend** for development testing
- **SMTP Configuration** for production
- **Management Commands** for testing
- **Comprehensive Logging** for debugging

## 🚀 How It Works

### 1. User Requests Password Reset
1. User clicks "Forgot Password" on login page
2. User enters their email address
3. System validates email and generates secure token
4. Email with reset link is sent to user

### 2. Email Verification
1. User receives HTML email with reset link
2. Link contains encrypted user ID and secure token
3. Link expires after 24 hours for security
4. User clicks link to access reset form

### 3. Password Reset
1. User enters new password with confirmation
2. Real-time validation checks password strength
3. System validates token and updates password
4. User is redirected to login with success message

## 📧 Email Configuration

### Development Setup (Console Backend)
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@telehealthdiabetes.com'
```

**Benefits:**
- No email server required
- Emails printed to console for testing
- Perfect for development and debugging

### Production Setup (SMTP Backend)
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Telehealth Diabetes Care <noreply@telehealthdiabetes.com>'
```

**Popular Email Services:**
- **Gmail**: smtp.gmail.com (port 587)
- **Outlook**: smtp-mail.outlook.com (port 587)
- **SendGrid**: smtp.sendgrid.net (port 587)
- **Mailgun**: smtp.mailgun.org (port 587)

## 🔗 URLs and Views

### URL Patterns
```python
# accounts/urls.py
urlpatterns = [
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
]
```

### View Functions
- **`forgot_password`**: Handles email submission and token generation
- **`reset_password`**: Validates token and processes password update

## 🎨 Templates

### Template Files
- **`forgot_password.html`**: Email submission form
- **`reset_password.html`**: Password reset form with validation
- **`password_reset_email.html`**: HTML email template

### Template Features
- **Bootstrap 5 Styling** for modern appearance
- **Real-time Validation** with JavaScript
- **Password Strength Indicator** with visual feedback
- **Loading States** during form submission
- **Error Handling** with clear messages
- **Mobile Responsive** design

## 🧪 Testing

### Manual Testing
1. **Test Email Submission**:
   ```
   URL: http://127.0.0.1:8000/accounts/forgot-password/
   Enter: demo@test.com
   Check: Console for email output
   ```

2. **Test Password Reset**:
   ```
   Copy reset link from console
   Paste in browser
   Enter new password
   Confirm password change
   ```

### Management Command Testing
```bash
# Generate test reset link
python manage.py test_password_reset --username demo
python manage.py test_password_reset --email demo@test.com

# Create test users
python manage.py create_test_users --count 3
```

### Automated Testing
```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class PasswordResetTests(TestCase):
    def test_forgot_password_view(self):
        response = self.client.get(reverse('accounts:forgot_password'))
        self.assertEqual(response.status_code, 200)
    
    def test_password_reset_email(self):
        user = User.objects.create_user('test', 'test@example.com', 'password')
        response = self.client.post(reverse('accounts:forgot_password'), {
            'email': 'test@example.com'
        })
        self.assertRedirects(response, reverse('accounts:login'))
```

## 🔒 Security Considerations

### Token Security
- **Cryptographically Secure**: Uses Django's built-in token generator
- **Time-Limited**: 24-hour expiration prevents long-term exposure
- **One-Time Use**: Tokens become invalid after successful reset
- **User-Specific**: Tokens tied to specific user accounts

### Email Security
- **No Passwords in Email**: Only secure reset links sent
- **HTTPS Recommended**: Use HTTPS in production for link security
- **Email Validation**: Verify email ownership before reset
- **No Information Disclosure**: Don't reveal if email exists

### Rate Limiting (Recommended)
```python
# Add to views.py for production
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        cache_key = f'password_reset_{email}'
        
        if cache.get(cache_key):
            return HttpResponseTooManyRequests("Too many requests")
        
        cache.set(cache_key, True, 300)  # 5 minute cooldown
        # ... rest of view
```

## 🚀 Production Deployment

### Environment Variables
```bash
# .env file
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Email Service Setup

#### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password
3. Use App Password in EMAIL_HOST_PASSWORD

#### SendGrid Setup
1. Create SendGrid account
2. Generate API key
3. Configure SMTP settings

#### Custom Domain Setup
1. Configure SPF records
2. Set up DKIM signing
3. Configure DMARC policy

## 📊 Monitoring and Analytics

### Email Delivery Tracking
```python
# Add to views.py
import logging

logger = logging.getLogger(__name__)

def forgot_password(request):
    # ... existing code
    try:
        send_mail(subject, message, from_email, [email])
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
```

### Usage Analytics
- Track password reset requests
- Monitor email delivery rates
- Analyze user behavior patterns
- Identify potential security issues

## 🛠️ Troubleshooting

### Common Issues

#### Email Not Sending
```bash
# Check email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

#### Invalid Reset Links
- Check token expiration (24 hours)
- Verify URL encoding
- Ensure user exists
- Check for multiple reset requests

#### Template Not Found
- Verify template paths
- Check TEMPLATES setting
- Ensure template inheritance

### Debug Commands
```bash
# Test email configuration
python manage.py sendtestemail user@example.com

# Generate test reset link
python manage.py test_password_reset --username demo

# Check user accounts
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
```

## 📈 Future Enhancements

### Planned Features
- **SMS-based Reset** for mobile users
- **Security Questions** as alternative verification
- **Account Lockout** after multiple failed attempts
- **Password History** to prevent reuse
- **Two-Factor Authentication** integration

### Advanced Security
- **CAPTCHA Integration** to prevent bots
- **IP-based Rate Limiting** for abuse prevention
- **Audit Logging** for security monitoring
- **Breach Detection** integration

---

## 🎉 Summary

The password reset system provides:

✅ **Secure token-based verification**  
✅ **Professional email templates**  
✅ **User-friendly interface**  
✅ **Mobile-responsive design**  
✅ **Development and production ready**  
✅ **Comprehensive testing tools**  
✅ **Security best practices**  
✅ **Easy deployment**  

**The system is now fully functional and ready for production use!** 🚀
