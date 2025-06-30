from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from support_groups.models import SupportGroup, GroupEvent
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with sample support groups'

    def handle(self, *args, **options):
        self.stdout.write('Creating support groups...')
        
        # Get or create admin user for group creation
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@diabetescare.co.ke', 'is_staff': True, 'is_superuser': True}
        )
        
        # Create support groups
        groups_data = [
            {
                'name': 'Type 1 Warriors Kenya',
                'description': 'A supportive community for people living with Type 1 diabetes in Kenya. Share experiences, tips, and encouragement with others who understand your journey.',
                'category': 'type1',
                'is_featured': True,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome to Type 1 Warriors Kenya! This is a safe space for people with Type 1 diabetes to connect and support each other.

Guidelines:
- Be respectful and supportive
- Share your experiences and learn from others
- No medical advice - share experiences only
- Keep discussions relevant to Type 1 diabetes
- Respect privacy and confidentiality''',
                'tags': 'type1, insulin, blood sugar, community, kenya'
            },
            {
                'name': 'Type 2 Diabetes Support Kisumu',
                'description': 'Local support group for Type 2 diabetes management in Kisumu and surrounding areas. Focus on lifestyle changes, medication management, and peer support.',
                'category': 'type2',
                'is_featured': True,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome to our Type 2 Diabetes Support group for Kisumu region!

Our focus:
- Lifestyle modifications and diet tips
- Exercise and physical activity
- Medication adherence
- Local resources and healthcare providers
- Emotional support and encouragement

Please be respectful and supportive of all members.''',
                'tags': 'type2, lifestyle, diet, exercise, kisumu, local'
            },
            {
                'name': 'Newly Diagnosed Support Circle',
                'description': 'A welcoming space for people recently diagnosed with diabetes. Get answers to your questions and support from those who have been there.',
                'category': 'newly_diagnosed',
                'is_featured': True,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome to our Newly Diagnosed Support Circle!

This group is specifically for:
- People diagnosed with diabetes in the last 2 years
- Those feeling overwhelmed or confused about their diagnosis
- Anyone seeking basic information and emotional support
- Family members and caregivers of newly diagnosed individuals

We're here to help you navigate this new journey with confidence.''',
                'tags': 'newly diagnosed, beginner, support, questions, guidance'
            },
            {
                'name': 'Diabetes Caregivers & Family',
                'description': 'Support group for family members, friends, and caregivers of people with diabetes. Learn how to provide the best support while taking care of yourself.',
                'category': 'caregivers',
                'is_featured': False,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome Caregivers and Family Members!

This group is for:
- Parents of children with diabetes
- Spouses and partners
- Family members and friends
- Professional caregivers

Topics we discuss:
- How to provide emotional support
- Understanding diabetes management
- Dealing with caregiver stress
- Emergency preparedness
- Communication strategies''',
                'tags': 'caregivers, family, parents, support, stress'
            },
            {
                'name': 'Young Adults with Diabetes (18-35)',
                'description': 'Connect with other young adults managing diabetes while navigating career, relationships, and life goals. Share experiences and strategies for success.',
                'category': 'teens_young_adults',
                'is_featured': False,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome Young Adults!

This group is for people aged 18-35 with diabetes who are:
- Starting careers or changing jobs
- In relationships or dating
- Planning families
- Pursuing education
- Traveling and exploring life

Let's support each other in living full, active lives with diabetes!''',
                'tags': 'young adults, career, relationships, travel, lifestyle'
            },
            {
                'name': 'Diabetes & Mental Health',
                'description': 'A safe space to discuss the emotional and mental health aspects of living with diabetes. Share coping strategies and find understanding.',
                'category': 'general',
                'is_featured': False,
                'is_public': True,
                'requires_approval': True,
                'guidelines': '''Welcome to our Mental Health Support Group!

This is a safe, moderated space to discuss:
- Diabetes burnout and fatigue
- Anxiety and depression related to diabetes
- Coping strategies and resilience
- Stress management techniques
- Professional mental health resources

Please note: This group requires approval to maintain a safe environment.
If you're in crisis, please contact emergency services or a mental health professional immediately.''',
                'tags': 'mental health, anxiety, depression, burnout, coping'
            },
            {
                'name': 'Diabetes Nutrition & Cooking',
                'description': 'Share healthy recipes, meal planning tips, and nutrition strategies for diabetes management. Learn from each other about local foods and cooking methods.',
                'category': 'general',
                'is_featured': False,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome to our Nutrition & Cooking group!

Share and learn about:
- Diabetes-friendly recipes
- Meal planning strategies
- Local Kenyan foods and diabetes
- Carbohydrate counting tips
- Budget-friendly healthy eating
- Cooking techniques and substitutions

Remember: Always consult with your healthcare provider or dietitian for personalized nutrition advice.''',
                'tags': 'nutrition, cooking, recipes, meal planning, local foods'
            },
            {
                'name': 'Diabetes & Exercise Enthusiasts',
                'description': 'For active people with diabetes who love to exercise, play sports, or stay fit. Share workout tips, blood sugar management during exercise, and motivation.',
                'category': 'general',
                'is_featured': False,
                'is_public': True,
                'requires_approval': False,
                'guidelines': '''Welcome Exercise Enthusiasts!

This group is for people with diabetes who:
- Love to exercise and stay active
- Play sports or participate in fitness activities
- Want to learn about blood sugar management during exercise
- Need motivation and workout buddies
- Want to share fitness achievements

Let's stay active and healthy together!''',
                'tags': 'exercise, fitness, sports, blood sugar, motivation'
            }
        ]
        
        created_groups = []
        for group_data in groups_data:
            group, created = SupportGroup.objects.get_or_create(
                name=group_data['name'],
                defaults={
                    'description': group_data['description'],
                    'category': group_data['category'],
                    'is_featured': group_data['is_featured'],
                    'is_public': group_data['is_public'],
                    'requires_approval': group_data['requires_approval'],
                    'guidelines': group_data['guidelines'],
                    'tags': group_data['tags'],
                    'created_by': admin_user,
                    'is_active': True
                }
            )
            
            if created:
                created_groups.append(group)
                self.stdout.write(f'Created group: {group.name}')
        
        self.stdout.write('Creating sample events...')
        
        # Create sample events
        events_data = [
            {
                'group_name': 'Type 1 Warriors Kenya',
                'title': 'Monthly Type 1 Check-in',
                'description': 'Monthly virtual meetup to share experiences, challenges, and victories. Open discussion format.',
                'event_type': 'meetup',
                'event_datetime': timezone.now() + timedelta(days=7, hours=19),  # Next week at 7 PM
                'duration_minutes': 90,
                'is_virtual': True,
                'max_participants': 50
            },
            {
                'group_name': 'Type 2 Diabetes Support Kisumu',
                'title': 'Healthy Cooking Workshop',
                'description': 'Learn to prepare diabetes-friendly meals using local ingredients. Hands-on cooking session.',
                'event_type': 'workshop',
                'event_datetime': timezone.now() + timedelta(days=14, hours=14),  # Two weeks at 2 PM
                'duration_minutes': 120,
                'is_virtual': False,
                'location': 'Kisumu Community Center',
                'max_participants': 20
            },
            {
                'group_name': 'Newly Diagnosed Support Circle',
                'title': 'Diabetes Basics Q&A Session',
                'description': 'Ask questions about diabetes management, medications, and lifestyle changes. Healthcare professional will be present.',
                'event_type': 'qa_session',
                'event_datetime': timezone.now() + timedelta(days=10, hours=18),  # 10 days at 6 PM
                'duration_minutes': 60,
                'is_virtual': True,
                'max_participants': 30
            },
            {
                'group_name': 'Diabetes & Exercise Enthusiasts',
                'title': 'Group Walk at Uhuru Park',
                'description': 'Join us for a group walk and learn about exercising safely with diabetes. All fitness levels welcome.',
                'event_type': 'activity',
                'event_datetime': timezone.now() + timedelta(days=5, hours=8),  # 5 days at 8 AM
                'duration_minutes': 60,
                'is_virtual': False,
                'location': 'Uhuru Park, Nairobi',
                'max_participants': 25
            }
        ]
        
        event_count = 0
        for event_data in events_data:
            try:
                group = SupportGroup.objects.get(name=event_data['group_name'])
                
                event, created = GroupEvent.objects.get_or_create(
                    group=group,
                    title=event_data['title'],
                    defaults={
                        'description': event_data['description'],
                        'event_type': event_data['event_type'],
                        'event_datetime': event_data['event_datetime'],
                        'duration_minutes': event_data['duration_minutes'],
                        'is_virtual': event_data['is_virtual'],
                        'location': event_data.get('location', ''),
                        'max_participants': event_data['max_participants'],
                        'created_by': admin_user
                    }
                )
                
                if created:
                    event_count += 1
                    self.stdout.write(f'Created event: {event.title}')
                    
            except SupportGroup.DoesNotExist:
                continue
        
        self.stdout.write(f'Created {len(created_groups)} support groups and {event_count} events')
        self.stdout.write(self.style.SUCCESS('Successfully populated support groups database'))
