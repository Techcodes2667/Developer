from django.urls import path
from . import views

app_name = 'providers'

urlpatterns = [
    path('dashboard/', views.provider_dashboard, name='dashboard'),
    path('patients/', views.patient_management, name='patients'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('schedule/', views.schedule_management, name='schedule'),
    path('messages/', views.message_center, name='messages'),
    path('profile/', views.provider_profile, name='profile'),
]
