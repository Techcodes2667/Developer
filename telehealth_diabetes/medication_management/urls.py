from django.urls import path
from . import views

app_name = 'medication_management'

urlpatterns = [
    path('', views.medication_list, name='list'),
    path('add/', views.add_medication, name='add'),
    path('log/', views.medication_log, name='log'),
    path('reminders/', views.reminders, name='reminders'),
    path('refills/', views.refill_requests, name='refills'),
    path('interactions/', views.check_interactions, name='interactions'),
    path('<int:medication_id>/', views.medication_detail, name='detail'),
    path('quick-log/', views.quick_log_medication, name='quick_log'),
]
