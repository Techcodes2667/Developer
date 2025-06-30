# Security Guidelines

This document outlines security best practices and guidelines for the Telehealth Diabetes Care System.

## Table of Contents
- [Security Overview](#security-overview)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Input Validation](#input-validation)
- [Session Management](#session-management)
- [API Security](#api-security)
- [Infrastructure Security](#infrastructure-security)
- [Monitoring & Incident Response](#monitoring--incident-response)
- [Compliance](#compliance)

## Security Overview

### Security Principles

The Telehealth Diabetes Care System follows these core security principles:

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Users have minimum necessary permissions
3. **Fail Secure**: System fails to a secure state
4. **Privacy by Design**: Privacy considerations built into system design
5. **Regular Updates**: Keep all components updated with security patches

### Threat Model

**Primary Threats:**
- Unauthorized access to patient health data
- Data breaches and privacy violations
- Account takeover attacks
- SQL injection and XSS attacks
- Man-in-the-middle attacks
- Denial of service attacks

**Assets to Protect:**
- Patient health records
- Authentication credentials
- Personal identifiable information (PII)
- Medical data and trends
- Communication between patients and providers

## Authentication & Authorization

### User Authentication

**Password Requirements:**
```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom password validator
class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain special character')
```

**Account Lockout:**
```python
# views.py
from django.contrib.auth import authenticate, login
from django.core.cache import cache
import time

def secure_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check for account lockout
        lockout_key = f"lockout_{username}"
        failed_attempts = cache.get(f"failed_attempts_{username}", 0)
        
        if cache.get(lockout_key):
            messages.error(request, 'Account temporarily locked. Try again later.')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Reset failed attempts on successful login
            cache.delete(f"failed_attempts_{username}")
            login(request, user)
            return redirect('patients:dashboard')
        else:
            # Increment failed attempts
            failed_attempts += 1
            cache.set(f"failed_attempts_{username}", failed_attempts, 300)  # 5 minutes
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                cache.set(lockout_key, True, 1800)  # 30 minutes lockout
                messages.error(request, 'Too many failed attempts. Account locked for 30 minutes.')
            else:
                messages.error(request, f'Invalid credentials. {5 - failed_attempts} attempts remaining.')
    
    return render(request, 'accounts/login.html')
```

**Two-Factor Authentication (2FA):**
```python
# Install: pip install django-otp qrcode[pil]

# settings.py
INSTALLED_APPS = [
    # ... other apps
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE = [
    # ... other middleware
    'django_otp.middleware.OTPMiddleware',
]

# views.py
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice

@otp_required
@login_required
def sensitive_view(request):
    # This view requires 2FA
    pass

def setup_2fa(request):
    if request.method == 'POST':
        device = TOTPDevice.objects.create(
            user=request.user,
            name='default',
            confirmed=True
        )
        # Generate QR code for user to scan
        qr_url = device.config_url
        return render(request, 'accounts/2fa_setup.html', {'qr_url': qr_url})
```

### Role-Based Access Control

**User Roles:**
```python
# models.py
class UserRole(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('provider', 'Healthcare Provider'),
        ('admin', 'Administrator'),
        ('support', 'Support Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permissions = models.JSONField(default=dict)

# Decorators for role-based access
def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                user_role = request.user.userrole.role
                if user_role not in allowed_roles:
                    raise PermissionDenied
            except UserRole.DoesNotExist:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@role_required(['provider', 'admin'])
def provider_dashboard(request):
    # Only providers and admins can access
    pass
```

## Data Protection

### Data Encryption

**Database Encryption:**
```python
# Install: pip install django-cryptography

# models.py
from django_cryptography.fields import encrypt

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Encrypt sensitive fields
    social_security_number = encrypt(models.CharField(max_length=11, blank=True))
    medical_record_number = encrypt(models.CharField(max_length=50, blank=True))
    emergency_contact_phone = encrypt(models.CharField(max_length=20))
```

**File Encryption:**
```python
# utils.py
from cryptography.fernet import Fernet
import os

class FileEncryption:
    def __init__(self):
        self.key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.key)
    
    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = self.cipher.encrypt(file_data)
        
        with open(file_path + '.encrypted', 'wb') as file:
            file.write(encrypted_data)
    
    def decrypt_file(self, encrypted_file_path):
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data
```

### Data Anonymization

**Patient Data Anonymization:**
```python
# utils.py
import hashlib
import random
import string

class DataAnonymizer:
    @staticmethod
    def anonymize_name(name):
        """Replace name with hash-based pseudonym"""
        hash_object = hashlib.sha256(name.encode())
        hex_dig = hash_object.hexdigest()
        return f"Patient_{hex_dig[:8]}"
    
    @staticmethod
    def anonymize_email(email):
        """Replace email with anonymized version"""
        username, domain = email.split('@')
        anonymized_username = ''.join(random.choices(string.ascii_lowercase, k=8))
        return f"{anonymized_username}@{domain}"
    
    @staticmethod
    def anonymize_phone(phone):
        """Replace phone with pattern-preserving anonymization"""
        digits = ''.join(filter(str.isdigit, phone))
        anonymized_digits = ''.join(random.choices(string.digits, k=len(digits)))
        return phone.replace(digits, anonymized_digits)

# Management command for data anonymization
class Command(BaseCommand):
    def handle(self, *args, **options):
        anonymizer = DataAnonymizer()
        
        for profile in PatientProfile.objects.all():
            profile.user.first_name = anonymizer.anonymize_name(profile.user.first_name)
            profile.user.last_name = anonymizer.anonymize_name(profile.user.last_name)
            profile.user.email = anonymizer.anonymize_email(profile.user.email)
            profile.emergency_contact_phone = anonymizer.anonymize_phone(profile.emergency_contact_phone)
            profile.user.save()
            profile.save()
```

## Input Validation

### Form Validation

**Secure Form Handling:**
```python
# forms.py
from django import forms
from django.core.validators import RegexValidator
import bleach

class SecurePatientForm(forms.ModelForm):
    # Phone number validation
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    emergency_contact_phone = forms.CharField(validators=[phone_validator])
    
    def clean_emergency_contact_name(self):
        name = self.cleaned_data['emergency_contact_name']
        # Sanitize HTML input
        clean_name = bleach.clean(name, tags=[], strip=True)
        
        # Validate name format
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', clean_name):
            raise forms.ValidationError('Name contains invalid characters')
        
        return clean_name
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Cross-field validation
        date_of_birth = cleaned_data.get('date_of_birth')
        if date_of_birth and date_of_birth > timezone.now().date():
            raise forms.ValidationError('Date of birth cannot be in the future')
        
        return cleaned_data
```

### SQL Injection Prevention

**Safe Database Queries:**
```python
# GOOD: Using Django ORM (automatically parameterized)
readings = BloodGlucoseReading.objects.filter(
    patient=patient_profile,
    recorded_at__gte=start_date
)

# GOOD: Using parameterized raw queries when necessary
from django.db import connection

def get_patient_stats(patient_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT AVG(value) FROM health_data_bloodglucosereading WHERE patient_id = %s",
            [patient_id]
        )
        return cursor.fetchone()[0]

# BAD: Never do this (vulnerable to SQL injection)
# cursor.execute(f"SELECT * FROM patients WHERE id = {user_input}")
```

### XSS Prevention

**Template Security:**
```html
<!-- Django templates auto-escape by default -->
<p>Patient name: {{ patient.name }}</p>  <!-- Safe -->

<!-- When you need to display HTML, use |safe carefully -->
<div>{{ content|safe }}</div>  <!-- Only if content is trusted -->

<!-- Use custom filters for specific formatting -->
<p>Phone: {{ patient.phone|phone_format }}</p>
```

**Content Security Policy:**
```python
# middleware.py
class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        response['Content-Security-Policy'] = csp_policy
        return response
```

## Session Management

### Secure Session Configuration

```python
# settings.py

# Session security
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour timeout

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Additional security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Session Monitoring

```python
# models.py
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

# middleware.py
class SessionTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Track user session
            session, created = UserSession.objects.get_or_create(
                user=request.user,
                session_key=request.session.session_key,
                defaults={
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
            
            # Update last activity
            session.last_activity = timezone.now()
            session.save()
            
            # Check for suspicious activity
            self.check_suspicious_activity(request, session)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def check_suspicious_activity(self, request, session):
        # Check for multiple concurrent sessions
        active_sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).count()
        
        if active_sessions > 3:  # Allow max 3 concurrent sessions
            # Log security event
            logger.warning(f"Multiple sessions detected for user {request.user.username}")
```

## API Security

### API Authentication

```python
# authentication.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from datetime import timedelta

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')

        # Check token expiration
        if token.created < timezone.now() - timedelta(hours=24):
            raise AuthenticationFailed('Token has expired.')

        return (token.user, token)
```

### Rate Limiting

```python
# Install: pip install django-ratelimit

from django_ratelimit.decorators import ratelimit
from django.http import HttpResponseTooManyRequests

@ratelimit(key='ip', rate='100/h', method='GET')
@ratelimit(key='user', rate='1000/h', method='GET')
def api_endpoint(request):
    if getattr(request, 'limited', None):
        return HttpResponseTooManyRequests('Rate limit exceeded')
    
    # API logic here
    pass

# Custom rate limiting for sensitive operations
@ratelimit(key='user', rate='10/h', method='POST')
def password_reset(request):
    # Limit password reset attempts
    pass
```

## Infrastructure Security

### Server Hardening

**Firewall Configuration:**
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Fail2ban for intrusion prevention
sudo apt install fail2ban

# Configure fail2ban
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log

[django-auth]
enabled = true
filter = django-auth
logpath = /opt/telehealth/logs/django.log
maxretry = 3
```

### Database Security

**PostgreSQL Security:**
```sql
-- Create read-only user for reporting
CREATE USER telehealth_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE telehealth_prod TO telehealth_readonly;
GRANT USAGE ON SCHEMA public TO telehealth_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO telehealth_readonly;

-- Enable row-level security
ALTER TABLE patients_patientprofile ENABLE ROW LEVEL SECURITY;

-- Create policy for patient data access
CREATE POLICY patient_data_policy ON patients_patientprofile
    FOR ALL TO telehealth_user
    USING (user_id = current_setting('app.current_user_id')::integer);
```

## Monitoring & Incident Response

### Security Monitoring

```python
# security_monitoring.py
import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

# Configure security logger
security_logger = logging.getLogger('security')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    security_logger.info(f"User login: {user.username} from {get_client_ip(request)}")

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    security_logger.warning(f"Failed login attempt: {credentials.get('username')} from {get_client_ip(request)}")

# Custom security events
def log_security_event(event_type, user, details, request=None):
    ip_address = get_client_ip(request) if request else 'unknown'
    security_logger.warning(f"Security event: {event_type} - User: {user} - IP: {ip_address} - Details: {details}")

# Usage in views
def sensitive_operation(request):
    try:
        # Perform operation
        pass
    except Exception as e:
        log_security_event('UNAUTHORIZED_ACCESS', request.user, str(e), request)
        raise
```

### Incident Response Plan

**Security Incident Response:**

1. **Detection**: Automated monitoring alerts
2. **Assessment**: Determine severity and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve

**Emergency Contacts:**
- Security Team: security@telehealthdiabetes.com
- System Administrator: admin@telehealthdiabetes.com
- Legal/Compliance: legal@telehealthdiabetes.com

## Compliance

### HIPAA Compliance

**Required Safeguards:**

1. **Administrative Safeguards:**
   - Security officer designation
   - Workforce training
   - Access management procedures
   - Incident response procedures

2. **Physical Safeguards:**
   - Facility access controls
   - Workstation security
   - Device and media controls

3. **Technical Safeguards:**
   - Access control
   - Audit controls
   - Integrity controls
   - Transmission security

**Implementation:**
```python
# Audit logging for HIPAA compliance
class HIPAAAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        db_table = 'hipaa_audit_log'

# Middleware for audit logging
class HIPAAAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log access to patient data
        if request.user.is_authenticated and 'patient' in request.path:
            HIPAAAuditLog.objects.create(
                user=request.user,
                action=request.method,
                resource_type='patient_data',
                resource_id=request.path,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response
```

### Data Retention Policy

```python
# management/commands/cleanup_old_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Clean up old data according to retention policy'

    def handle(self, *args, **options):
        # Delete audit logs older than 7 years (HIPAA requirement)
        seven_years_ago = timezone.now() - timedelta(days=7*365)
        HIPAAAuditLog.objects.filter(timestamp__lt=seven_years_ago).delete()
        
        # Delete inactive user sessions older than 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        UserSession.objects.filter(
            last_activity__lt=thirty_days_ago,
            is_active=False
        ).delete()
        
        self.stdout.write(self.style.SUCCESS('Data cleanup completed'))
```

---

**Security Questions?** Contact our security team at oongugucodes@gmail.com
