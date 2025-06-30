from django.urls import path
from . import views

app_name = 'health_data'

urlpatterns = [
    path('', views.health_data_home, name='home'),
    path('glucose/', views.glucose_tracking, name='glucose'),
    path('weight/', views.weight_tracking, name='weight'),
    path('activity/', views.activity_tracking, name='activity'),
    path('reports/', views.health_reports, name='reports'),
]
