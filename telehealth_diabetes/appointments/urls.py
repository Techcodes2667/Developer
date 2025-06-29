from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('schedule/', views.schedule, name='schedule'),
    path('list/', views.appointment_list, name='list'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='detail'),
]
