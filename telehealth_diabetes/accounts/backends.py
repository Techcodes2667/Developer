from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.conf import settings
import hashlib


class UltraFastAuthBackend(BaseBackend):
    """
    Ultra-fast authentication backend for development.
    Bypasses most of Django's authentication overhead.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Direct database query with minimal fields
            user = User.objects.only('id', 'username', 'password', 'is_active').get(
                username=username
            )
            
            if not user.is_active:
                return None
            
            # Ultra-fast password check for development
            if settings.DEBUG:
                # For development: simple MD5 check (INSECURE but fast)
                if user.password.startswith('md5$'):
                    # Extract hash from Django's format: md5$salt$hash
                    stored_hash = user.password.split('$')[-1]
                    if len(stored_hash) == 32:  # MD5 hash length
                        # Simple MD5 comparison for speed
                        test_hash = hashlib.md5(password.encode()).hexdigest()
                        if test_hash == stored_hash:
                            return user
                
                # Fallback to Django's check_password for other formats
                if check_password(password, user.password):
                    return user
            else:
                # Production: use Django's secure password checking
                if check_password(password, user.password):
                    return user
                    
        except User.DoesNotExist:
            # Fake password check to prevent timing attacks
            if settings.DEBUG:
                hashlib.md5(b'fake_password').hexdigest()
            else:
                check_password('fake_password', 'fake_hash')
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.only('id', 'username', 'is_active').get(pk=user_id)
        except User.DoesNotExist:
            return None


class InstantAuthBackend(BaseBackend):
    """
    Instant authentication for development testing.
    WARNING: COMPLETELY INSECURE - DEVELOPMENT ONLY!
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not settings.DEBUG:
            return None  # Only works in development
            
        if username is None:
            return None
        
        try:
            # Instant authentication - no password check!
            user = User.objects.only('id', 'username', 'is_active').get(
                username=username
            )
            
            if user.is_active:
                return user
                
        except User.DoesNotExist:
            pass
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.only('id', 'username', 'is_active').get(pk=user_id)
        except User.DoesNotExist:
            return None
