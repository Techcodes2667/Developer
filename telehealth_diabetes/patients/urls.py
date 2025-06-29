from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('monitoring/', views.monitoring, name='monitoring'),
    path('portal/', views.portal, name='portal'),
]
