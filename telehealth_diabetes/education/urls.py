from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.education_home, name='home'),
    path('library/', views.content_library, name='library'),
    path('search/', views.search_content, name='search'),
    path('my-progress/', views.my_progress, name='my_progress'),
    path('category/<int:category_id>/', views.category_content, name='category'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
    path('bookmark/<int:content_id>/', views.bookmark_content, name='bookmark'),
    path('recipes/', views.recipe_list, name='recipes'),
    path('recipes/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('exercises/', views.exercise_list, name='exercises'),
    path('exercises/<slug:slug>/', views.exercise_detail, name='exercise_detail'),
]
