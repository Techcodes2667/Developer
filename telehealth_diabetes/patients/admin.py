from django.contrib import admin
from .models import PatientProfile, PatientNote

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'diabetes_type', 'diagnosis_date', 'age', 'created_at']
    list_filter = ['diabetes_type', 'gender', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'phone_number', 'address')
        }),
        ('Diabetes Information', {
            'fields': ('diabetes_type', 'diagnosis_date', 'hba1c_target',
                      'blood_glucose_target_min', 'blood_glucose_target_max')
        }),
        ('Healthcare Provider', {
            'fields': ('primary_doctor', 'healthcare_facility')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'notification_preferences')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    list_display = ['patient', 'provider', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['patient__user__username', 'provider__username', 'note']
    readonly_fields = ['created_at', 'updated_at']
