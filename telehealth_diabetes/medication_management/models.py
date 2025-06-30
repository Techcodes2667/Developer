from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from patients.models import PatientProfile

class Medication(models.Model):
    """Master medication database"""
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    medication_type = models.CharField(max_length=50, choices=[
        ('insulin', 'Insulin'),
        ('metformin', 'Metformin'),
        ('sulfonylurea', 'Sulfonylurea'),
        ('dpp4', 'DPP-4 Inhibitor'),
        ('sglt2', 'SGLT-2 Inhibitor'),
        ('glp1', 'GLP-1 Agonist'),
        ('other', 'Other'),
    ])
    description = models.TextField(blank=True)
    common_side_effects = models.TextField(blank=True)
    warnings = models.TextField(blank=True)

    def __str__(self):
        return self.name

class PatientMedication(models.Model):
    """Medications prescribed to patients"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medications')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg, 10 units")
    frequency = models.CharField(max_length=100, help_text="e.g., twice daily, before meals")
    instructions = models.TextField(blank=True)
    prescribed_by = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_active', 'medication__name']

    def __str__(self):
        return f"{self.patient.user.username} - {self.medication.name} ({self.dosage})"

class MedicationReminder(models.Model):
    """Medication reminders for patients"""
    patient_medication = models.ForeignKey(PatientMedication, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    days_of_week = models.CharField(max_length=20, default='1234567', help_text="1=Monday, 7=Sunday")

    def __str__(self):
        return f"{self.patient_medication.medication.name} reminder at {self.reminder_time}"

class MedicationLog(models.Model):
    """Log of medication taken by patients"""
    patient_medication = models.ForeignKey(PatientMedication, on_delete=models.CASCADE, related_name='logs')
    taken_at = models.DateTimeField()
    dosage_taken = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    was_reminder = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"{self.patient_medication.medication.name} taken at {self.taken_at}"

class MedicationRefillRequest(models.Model):
    """Refill requests for medications"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('completed', 'Completed'),
    ]

    patient_medication = models.ForeignKey(PatientMedication, on_delete=models.CASCADE, related_name='refill_requests')
    pharmacy_name = models.CharField(max_length=200, blank=True)
    pharmacy_phone = models.CharField(max_length=15, blank=True)
    quantity_requested = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refills')

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Refill request for {self.patient_medication.medication.name} - {self.status}"

class DrugInteraction(models.Model):
    """Drug interaction warnings"""
    medication1 = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='interactions_as_med1')
    medication2 = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='interactions_as_med2')
    severity = models.CharField(max_length=20, choices=[
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('severe', 'Severe'),
    ])
    description = models.TextField()
    recommendation = models.TextField(blank=True)

    class Meta:
        unique_together = ['medication1', 'medication2']

    def __str__(self):
        return f"{self.medication1.name} + {self.medication2.name} ({self.severity})"
