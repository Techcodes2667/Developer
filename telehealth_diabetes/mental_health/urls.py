from django.urls import path
from . import views

app_name = 'mental_health'

urlpatterns = [
    path('', views.mental_health_home, name='home'),
    path('dashboard/', views.wellness_dashboard, name='dashboard'),
    path('resources/', views.resource_list, name='resources'),
    path('assessments/', views.assessment_list, name='assessments'),
    path('assessments/<int:assessment_id>/', views.take_assessment, name='take_assessment'),
    path('assessment-results/', views.assessment_results, name='assessment_results'),
    path('mood-tracking/', views.mood_tracking, name='mood_tracking'),
    path('quick-mood-check/', views.quick_mood_check, name='quick_mood_check'),
    path('coping-strategies/', views.coping_strategies, name='coping_strategies'),
    path('crisis-resources/', views.crisis_resources, name='crisis_resources'),
]
