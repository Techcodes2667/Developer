from django.contrib import admin
from .models import (
    EducationCategory, EducationContent, PatientProgress,
    Recipe, ExerciseRoutine
)

@admin.register(EducationCategory)
class EducationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

@admin.register(EducationContent)
class EducationContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'difficulty_level', 'is_published', 'view_count']
    list_filter = ['category', 'content_type', 'difficulty_level', 'is_published', 'is_featured']
    search_fields = ['title', 'summary', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'content_type', 'difficulty_level')
        }),
        ('Content', {
            'fields': ('summary', 'content', 'video_url', 'image')
        }),
        ('Metadata', {
            'fields': ('author', 'tags', 'estimated_read_time')
        }),
        ('Targeting', {
            'fields': ('diabetes_types', 'target_audience')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'meal_type', 'difficulty_level', 'servings', 'total_time_minutes', 'is_published']
    list_filter = ['meal_type', 'difficulty_level', 'is_published']
    search_fields = ['title', 'description', 'ingredients']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ExerciseRoutine)
class ExerciseRoutineAdmin(admin.ModelAdmin):
    list_display = ['title', 'intensity_level', 'duration_minutes', 'suitable_for_beginners', 'is_published']
    list_filter = ['intensity_level', 'suitable_for_beginners', 'requires_supervision', 'is_published']
    search_fields = ['title', 'description', 'instructions']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(PatientProgress)
class PatientProgressAdmin(admin.ModelAdmin):
    list_display = ['patient', 'content', 'progress_percentage', 'is_completed', 'started_at']
    list_filter = ['content__category', 'started_at', 'completed_at']
    search_fields = ['patient__user__username', 'content__title']
