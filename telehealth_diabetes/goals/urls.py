from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.goals_home, name='home'),
    path('dashboard/', views.goals_dashboard, name='dashboard'),
    path('list/', views.goal_list, name='list'),
    path('create/', views.create_goal, name='create'),
    path('<int:goal_id>/', views.goal_detail, name='detail'),
    path('<int:goal_id>/update/', views.update_progress, name='update_progress'),
    path('<int:goal_id>/pause/', views.pause_goal, name='pause'),
    path('<int:goal_id>/delete/', views.delete_goal, name='delete'),
    path('quick-update/', views.quick_progress_update, name='quick_update'),
    path('achievements/', views.achievements, name='achievements'),
    path('templates/', views.goal_templates, name='templates'),
]
