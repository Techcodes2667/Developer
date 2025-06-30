from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Public-facing pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-telehealth-works/', views.how_telehealth_works, name='how_telehealth_works'),
    path('diabetes-info/', views.diabetes_info_hub, name='diabetes_info_hub'),
    path('tele-education-overview/', views.tele_education_overview, name='tele_education_overview'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),

    # Legal & Security pages
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-of-service/', views.terms, name='terms'),
    path('security-tips/', views.security_tips, name='security_tips'),

    # Authentication
    path('signup/', views.register_view, name='signup'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Other
    path('community/', views.community, name='community'),
    path('health/', views.health_check, name='health_check'),
]
