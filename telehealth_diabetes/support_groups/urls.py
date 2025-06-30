from django.urls import path
from . import views

app_name = 'support_groups'

urlpatterns = [
    path('', views.support_groups_home, name='home'),
    path('browse/', views.group_list, name='list'),
    path('my-groups/', views.my_groups, name='my_groups'),
    path('create/', views.create_group, name='create'),
    path('<int:group_id>/', views.group_detail, name='detail'),
    path('<int:group_id>/join/', views.join_group, name='join'),
    path('<int:group_id>/leave/', views.leave_group, name='leave'),
    path('<int:group_id>/discussions/', views.group_discussions, name='discussions'),
    path('<int:group_id>/discussions/<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:group_id>/events/', views.group_events, name='events'),
    path('qa-sessions/', views.qa_sessions, name='qa_sessions'),
]
