from django.contrib import admin
from .models import (
    Medication, PatientMedication, MedicationReminder,
    MedicationLog, MedicationRefillRequest, DrugInteraction
)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'medication_type']
    list_filter = ['medication_type']
    search_fields = ['name', 'generic_name']
    ordering = ['name']

@admin.register(PatientMedication)
class PatientMedicationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medication', 'dosage', 'frequency', 'is_active', 'start_date']
    list_filter = ['is_active', 'medication__medication_type', 'start_date']
    search_fields = ['patient__user__username', 'medication__name', 'prescribed_by']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Patient & Medication', {
            'fields': ('patient', 'medication')
        }),
        ('Dosage Information', {
            'fields': ('dosage', 'frequency', 'instructions')
        }),
        ('Prescription Details', {
            'fields': ('prescribed_by', 'start_date', 'end_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = ['patient_medication', 'taken_at', 'dosage_taken', 'was_reminder']
    list_filter = ['taken_at', 'was_reminder']
    search_fields = ['patient_medication__patient__user__username', 'patient_medication__medication__name']
    date_hierarchy = 'taken_at'

@admin.register(MedicationReminder)
class MedicationReminderAdmin(admin.ModelAdmin):
    list_display = ['patient_medication', 'reminder_time', 'is_active', 'days_of_week']
    list_filter = ['is_active', 'reminder_time']
    search_fields = ['patient_medication__patient__user__username', 'patient_medication__medication__name']

@admin.register(MedicationRefillRequest)
class MedicationRefillRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_medication', 'status', 'requested_at', 'pharmacy_name']
    list_filter = ['status', 'requested_at']
    search_fields = ['patient_medication__patient__user__username', 'patient_medication__medication__name', 'pharmacy_name']
    readonly_fields = ['requested_at']

@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = ['medication1', 'medication2', 'severity']
    list_filter = ['severity']
    search_fields = ['medication1__name', 'medication2__name']
