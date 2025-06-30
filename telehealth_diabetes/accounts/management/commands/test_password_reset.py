from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class Command(BaseCommand):
    help = 'Test password reset functionality by generating a reset link for a user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address of the user to generate reset link for'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the user to generate reset link for'
        )

    def handle(self, *args, **options):
        email = options.get('email')
        username = options.get('username')
        
        if not email and not username:
            self.stdout.write(
                self.style.ERROR('Please provide either --email or --username')
            )
            return
        
        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(username=username)
                
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = f"http://127.0.0.1:8000/accounts/reset-password/{uid}/{token}/"
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Password reset link generated for user: {user.username}')
            )
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'👤 Name: {user.first_name} {user.last_name}')
            self.stdout.write(f'\n🔗 Reset Link:')
            self.stdout.write(f'{reset_link}')
            self.stdout.write(f'\n⏰ This link will expire in 24 hours.')
            self.stdout.write(f'\n📋 To test:')
            self.stdout.write(f'   1. Copy the link above')
            self.stdout.write(f'   2. Paste it in your browser')
            self.stdout.write(f'   3. Enter a new password')
            self.stdout.write(f'   4. Try logging in with the new password')
            
        except User.DoesNotExist:
            if email:
                self.stdout.write(
                    self.style.ERROR(f'❌ No user found with email: {email}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ No user found with username: {username}')
                )
            
            self.stdout.write(f'\n💡 Available users:')
            users = User.objects.all()[:5]
            for user in users:
                self.stdout.write(f'   - {user.username} ({user.email})')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
