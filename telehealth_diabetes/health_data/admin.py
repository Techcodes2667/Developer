from django.contrib import admin
from .models import (
    BloodGlucoseReading, WeightReading, BloodPressureReading,
    CarbIntakeRecord, ActivityRecord, SleepRecord
)

@admin.register(BloodGlucoseReading)
class BloodGlucoseReadingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'value', 'measurement_type', 'measured_at', 'created_at']
    list_filter = ['measurement_type', 'measured_at', 'created_at']
    search_fields = ['patient__user__username']
    date_hierarchy = 'measured_at'

@admin.register(WeightReading)
class WeightReadingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'weight', 'measured_at', 'created_at']
    list_filter = ['measured_at', 'created_at']
    search_fields = ['patient__user__username']
    date_hierarchy = 'measured_at'

@admin.register(BloodPressureReading)
class BloodPressureReadingAdmin(admin.ModelAdmin):
    list_display = ['patient', 'systolic', 'diastolic', 'measured_at', 'created_at']
    list_filter = ['measured_at', 'created_at']
    search_fields = ['patient__user__username']
    date_hierarchy = 'measured_at'

@admin.register(CarbIntakeRecord)
class CarbIntakeRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'carbs_grams', 'meal_type', 'recorded_at']
    list_filter = ['meal_type', 'recorded_at']
    search_fields = ['patient__user__username', 'food_description']

@admin.register(ActivityRecord)
class ActivityRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'activity_type', 'duration_minutes', 'intensity', 'recorded_at']
    list_filter = ['activity_type', 'intensity', 'recorded_at']
    search_fields = ['patient__user__username', 'description']

@admin.register(SleepRecord)
class SleepRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'sleep_start', 'sleep_end', 'duration_hours', 'quality']
    list_filter = ['quality', 'sleep_start']
    search_fields = ['patient__user__username']
