from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('schedule/', views.schedule, name='schedule'),
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/join/', views.join_appointment, name='join'),
    path('<int:appointment_id>/feedback/', views.appointment_feedback, name='feedback'),
    path('<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule'),
    path('api/provider/<int:provider_id>/availability/', views.get_provider_availability, name='provider_availability'),
]
