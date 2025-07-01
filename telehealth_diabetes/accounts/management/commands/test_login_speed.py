from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.test import Client
import time
import statistics


class Command(BaseCommand):
    help = 'Test login performance and speed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=10,
            help='Number of test iterations to run'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='demo',
            help='Username to test with'
        )

    def handle(self, *args, **options):
        iterations = options['iterations']
        username = options['username']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Testing login performance with {iterations} iterations...')
        )
        
        # Ensure test user exists
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'✅ Test user "{username}" found')
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Test user "{username}" not found. Creating one...')
            )
            user = User.objects.create_user(
                username=username,
                password='demo123',
                email=f'{username}@test.com'
            )
            self.stdout.write(f'✅ Created test user "{username}"')

        # Test password hashing speed
        self.stdout.write('\n📊 Testing password hashing speed...')
        hash_times = []
        for i in range(iterations):
            start_time = time.time()
            check_password('demo123', user.password)
            end_time = time.time()
            hash_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_hash_time = statistics.mean(hash_times)
        min_hash_time = min(hash_times)
        max_hash_time = max(hash_times)
        
        self.stdout.write(f'   Average hash time: {avg_hash_time:.2f}ms')
        self.stdout.write(f'   Min hash time: {min_hash_time:.2f}ms')
        self.stdout.write(f'   Max hash time: {max_hash_time:.2f}ms')
        
        # Test database query speed
        self.stdout.write('\n📊 Testing database query speed...')
        query_times = []
        for i in range(iterations):
            start_time = time.time()
            User.objects.only('id', 'username', 'password', 'first_name', 'is_active').get(
                username=username, is_active=True
            )
            end_time = time.time()
            query_times.append((end_time - start_time) * 1000)
        
        avg_query_time = statistics.mean(query_times)
        min_query_time = min(query_times)
        max_query_time = max(query_times)
        
        self.stdout.write(f'   Average query time: {avg_query_time:.2f}ms')
        self.stdout.write(f'   Min query time: {min_query_time:.2f}ms')
        self.stdout.write(f'   Max query time: {max_query_time:.2f}ms')
        
        # Test full login flow
        self.stdout.write('\n📊 Testing full login flow...')
        client = Client()
        login_times = []
        
        for i in range(iterations):
            start_time = time.time()
            response = client.post('/accounts/fast-login/', {
                'username': username,
                'password': 'demo123'
            })
            end_time = time.time()
            login_times.append((end_time - start_time) * 1000)
            
            # Logout for next iteration
            client.logout()
        
        avg_login_time = statistics.mean(login_times)
        min_login_time = min(login_times)
        max_login_time = max(login_times)
        
        self.stdout.write(f'   Average login time: {avg_login_time:.2f}ms')
        self.stdout.write(f'   Min login time: {min_login_time:.2f}ms')
        self.stdout.write(f'   Max login time: {max_login_time:.2f}ms')
        
        # Performance analysis
        self.stdout.write('\n📈 Performance Analysis:')
        total_time = avg_hash_time + avg_query_time
        
        if avg_login_time < 100:
            self.stdout.write(self.style.SUCCESS('🚀 EXCELLENT: Login is very fast!'))
        elif avg_login_time < 300:
            self.stdout.write(self.style.SUCCESS('✅ GOOD: Login speed is acceptable'))
        elif avg_login_time < 1000:
            self.stdout.write(self.style.WARNING('⚠️  SLOW: Login could be faster'))
        else:
            self.stdout.write(self.style.ERROR('❌ VERY SLOW: Login needs optimization'))
        
        # Recommendations
        self.stdout.write('\n💡 Recommendations:')
        if avg_hash_time > 50:
            self.stdout.write('   - Consider using faster password hasher for development')
        if avg_query_time > 10:
            self.stdout.write('   - Database queries could be optimized')
        if avg_login_time > 200:
            self.stdout.write('   - Consider implementing caching')
            self.stdout.write('   - Review middleware and session handling')
        
        self.stdout.write(f'\n🎯 Total estimated login time: {total_time:.2f}ms')
        self.stdout.write(
            self.style.SUCCESS('✅ Performance test completed!')
        )
