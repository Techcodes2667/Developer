from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Create test users for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of test users to create (default: 5)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(
            self.style.SUCCESS(f'Creating {count} test users...')
        )

        test_users = [
            {
                'username': 'testpatient',
                'email': 'patient@test.com',
                'first_name': 'Test',
                'last_name': 'Patient',
                'password': 'testpass123'
            },
            {
                'username': 'testdoctor',
                'email': 'doctor@test.com',
                'first_name': 'Dr. Test',
                'last_name': 'Doctor',
                'password': 'testpass123'
            },
            {
                'username': 'testnurse',
                'email': 'nurse@test.com',
                'first_name': 'Test',
                'last_name': 'Nurse',
                'password': 'testpass123'
            },
            {
                'username': 'testadmin',
                'email': 'admin@test.com',
                'first_name': 'Test',
                'last_name': 'Admin',
                'password': 'testpass123'
            },
            {
                'username': 'demo',
                'email': 'demo@test.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'password': 'demo123'
            }
        ]

        created_count = 0
        
        with transaction.atomic():
            for i, user_data in enumerate(test_users[:count]):
                username = user_data['username']
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User "{username}" already exists, skipping...')
                    )
                    continue
                
                # Create user
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password=user_data['password']
                )
                
                # Make testadmin a superuser
                if username == 'testadmin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username} (password: {user_data["password"]})')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} test users!')
        )
        
        if created_count > 0:
            self.stdout.write(
                self.style.WARNING('\nTest User Credentials:')
            )
            for user_data in test_users[:count]:
                if not User.objects.filter(username=user_data['username']).exists():
                    continue
                self.stdout.write(f"  Username: {user_data['username']}")
                self.stdout.write(f"  Password: {user_data['password']}")
                self.stdout.write(f"  Email: {user_data['email']}")
                self.stdout.write("  ---")
            
            self.stdout.write(
                self.style.SUCCESS('\nYou can now use these credentials to test login functionality!')
            )
