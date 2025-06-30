from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def home(request):
    """Home page view - Central entry point with hero section and value proposition"""
    # Get featured content for homepage
    try:
        from education.models import EducationContent
        from appointments.models import HealthcareProvider
        featured_content = EducationContent.objects.filter(is_published=True, is_featured=True)[:3]
        provider_count = HealthcareProvider.objects.filter(is_available=True).count()
    except ImportError:
        featured_content = []
        provider_count = 0

    context = {
        'featured_content': featured_content,
        'provider_count': provider_count,
        'hero_title': 'Empowering Diabetes Management from Kisumu – Anywhere, Anytime',
        'hero_subtitle': 'Comprehensive telehealth platform for diabetes care, education, and community support',
    }
    return render(request, 'main/home.html', context)

def about(request):
    """About page view"""
    return render(request, 'main/about.html')

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        contact_name = request.POST.get('name')
        contact_email = request.POST.get('email')
        contact_message = request.POST.get('message')

        # Here you would typically send an email or save to database
        # For now, just show success message
        if contact_name and contact_email and contact_message:
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('main:contact')

    return render(request, 'main/contact.html')

def privacy(request):
    """Privacy policy page"""
    return render(request, 'main/privacy.html')

def terms(request):
    """Terms of service page"""
    return render(request, 'main/terms.html')

def register_view(request):
    """User registration - redirect to accounts app"""
    return redirect('accounts:register')

def login_view(request):
    """User login - redirect to accounts app"""
    return redirect('accounts:login')

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

def how_telehealth_works(request):
    """How Telehealth Works page - Explains telehealth concepts and benefits"""
    context = {
        'telehealth_benefits': [
            'Improved access to care for rural communities in Kisumu County',
            'Increased convenience for patients',
            'Enhanced patient engagement',
            'Reduced healthcare costs',
            'Real-time health monitoring',
        ],
        'telehealth_taxonomy': [
            {'name': 'Tele-Education', 'description': 'Educational resources and learning modules'},
            {'name': 'Interactive Patient Care', 'description': 'Real-time consultations and monitoring'},
            {'name': 'Telemedicine', 'description': 'Virtual medical consultations'},
            {'name': 'Remote Patient Monitoring', 'description': 'Continuous health data tracking'},
            {'name': 'Store and Forward', 'description': 'Asynchronous data sharing'},
            {'name': 'Patient Portal', 'description': 'Centralized health management platform'},
        ]
    }
    return render(request, 'main/how_telehealth_works.html', context)

def diabetes_info_hub(request):
    """Diabetes Info Hub - Comprehensive diabetes information"""
    context = {
        'diabetes_types': [
            {
                'name': 'Type 1 Diabetes',
                'description': 'Autoimmune condition where the body attacks insulin-producing cells',
                'key_points': ['Usually diagnosed in childhood', 'Requires insulin therapy', 'Represents 5-10% of cases']
            },
            {
                'name': 'Type 2 Diabetes',
                'description': 'Most common form where the body becomes resistant to insulin',
                'key_points': ['Often develops in adulthood', 'Linked to lifestyle factors', 'Represents 90-95% of cases']
            },
            {
                'name': 'Gestational Diabetes',
                'description': 'Diabetes that develops during pregnancy',
                'key_points': ['Occurs during pregnancy', 'Usually resolves after birth', 'Increases future diabetes risk']
            }
        ],
        'risk_factors': [
            'Family history of diabetes',
            'Overweight or obesity',
            'Physical inactivity',
            'Age over 45',
            'High blood pressure',
            'Abnormal cholesterol levels'
        ],
        'common_symptoms': [
            'Increased thirst and urination',
            'Unexplained weight loss',
            'Fatigue and weakness',
            'Blurred vision',
            'Slow-healing wounds',
            'Frequent infections'
        ]
    }
    return render(request, 'main/diabetes_info_hub.html', context)

def tele_education_overview(request):
    """Tele-Education Overview - Showcases educational features"""
    try:
        from education.models import EducationCategory, EducationContent
        categories = EducationCategory.objects.filter(is_active=True)[:6]
        sample_content = EducationContent.objects.filter(is_published=True)[:6]
    except ImportError:
        categories = []
        sample_content = []

    context = {
        'categories': categories,
        'sample_content': sample_content,
        'education_features': [
            'Comprehensive diabetes education library',
            'Interactive learning modules',
            'Personalized content recommendations',
            'Progress tracking and certificates',
            'Expert-reviewed materials',
            'Local context for Kisumu region'
        ]
    }
    return render(request, 'main/tele_education_overview.html', context)

def faq(request):
    """FAQ page"""
    faqs = [
        {
            'category': 'General Use',
            'questions': [
                {
                    'question': 'How do I get started with the platform?',
                    'answer': 'Simply create an account, complete your profile, and start exploring our educational resources and booking appointments.'
                },
                {
                    'question': 'Is this platform free to use?',
                    'answer': 'Basic educational resources are free. Consultations with healthcare providers may have associated fees.'
                }
            ]
        },
        {
            'category': 'Technical Support',
            'questions': [
                {
                    'question': 'What devices can I use to access the platform?',
                    'answer': 'Our platform works on computers, tablets, and smartphones with internet access.'
                },
                {
                    'question': 'What if I have technical difficulties during a consultation?',
                    'answer': 'Our support team is available to help. Contact us immediately if you experience issues.'
                }
            ]
        },
        {
            'category': 'Privacy & Security',
            'questions': [
                {
                    'question': 'How is my health data protected?',
                    'answer': 'We use industry-standard encryption and comply with healthcare privacy regulations to protect your data.'
                },
                {
                    'question': 'Who can see my health information?',
                    'answer': 'Only you and your assigned healthcare providers can access your health data.'
                }
            ]
        }
    ]
    return render(request, 'main/faq.html', {'faqs': faqs})

def blog(request):
    """News & Blog page"""
    # This would typically fetch from a blog model
    blog_posts = [
        {
            'title': 'Managing Diabetes During Rainy Season in Kisumu',
            'excerpt': 'Tips for maintaining your diabetes care routine during the rainy season.',
            'date': '2024-01-15',
            'category': 'Lifestyle Tips'
        },
        {
            'title': 'New Research on Diabetes Prevention',
            'excerpt': 'Latest findings on preventing Type 2 diabetes through lifestyle changes.',
            'date': '2024-01-10',
            'category': 'Research'
        },
        {
            'title': 'Platform Update: New Features Available',
            'excerpt': 'Exciting new features to help you manage your diabetes better.',
            'date': '2024-01-05',
            'category': 'Platform Updates'
        }
    ]
    return render(request, 'main/blog.html', {'blog_posts': blog_posts})

def security_tips(request):
    """Security Tips page"""
    security_tips = [
        {
            'title': 'Use Strong Passwords',
            'description': 'Create unique, complex passwords for your account and enable two-factor authentication when available.'
        },
        {
            'title': 'Keep Software Updated',
            'description': 'Ensure your device and browser are up to date with the latest security patches.'
        },
        {
            'title': 'Secure Internet Connection',
            'description': 'Always use secure, private internet connections when accessing your health information.'
        },
        {
            'title': 'Log Out Properly',
            'description': 'Always log out of your account when finished, especially on shared devices.'
        },
        {
            'title': 'Be Cautious with Personal Information',
            'description': 'Never share your login credentials and be wary of phishing attempts.'
        }
    ]
    return render(request, 'main/security_tips.html', {'security_tips': security_tips})
