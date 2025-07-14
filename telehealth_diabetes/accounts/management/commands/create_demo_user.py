from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create demo user for testing'

    def handle(self, *args, **options):
        # Create demo user
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@test.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS('✅ Created demo user: demo/demo123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Demo user already exists')
            )
        
        # Create test patient
        user2, created2 = User.objects.get_or_create(
            username='testpatient',
            defaults={
                'email': 'testpatient@test.com',
                'first_name': 'Test',
                'last_name': 'Patient',
                'is_active': True,
            }
        )
        
        if created2:
            user2.set_password('testpass123')
            user2.save()
            self.stdout.write(
                self.style.SUCCESS('✅ Created test patient: testpatient/testpass123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Test patient already exists')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Total users: {User.objects.count()}')
        )
