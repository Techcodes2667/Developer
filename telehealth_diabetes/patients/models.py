from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class PatientProfile(models.Model):
    """Extended patient profile with diabetes-specific information"""
    DIABETES_TYPES = [
        ('type1', 'Type 1 Diabetes'),
        ('type2', 'Type 2 Diabetes'),
        ('gestational', 'Gestational Diabetes'),
        ('other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    # Diabetes-specific fields
    diabetes_type = models.CharField(max_length=20, choices=DIABETES_TYPES, blank=True)
    diagnosis_date = models.DateField(null=True, blank=True)
    hba1c_target = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(4.0), MaxValueValidator(15.0)],
        help_text="Target HbA1c percentage"
    )
    blood_glucose_target_min = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(3.0), MaxValueValidator(30.0)],
        help_text="Target minimum blood glucose (mmol/L)"
    )
    blood_glucose_target_max = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(3.0), MaxValueValidator(30.0)],
        help_text="Target maximum blood glucose (mmol/L)"
    )

    # Healthcare provider
    primary_doctor = models.CharField(max_length=100, blank=True)
    healthcare_facility = models.CharField(max_length=200, blank=True)

    # Preferences
    preferred_language = models.CharField(max_length=20, default='en')
    notification_preferences = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_diabetes_type_display()}"

    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class PatientNote(models.Model):
    """Notes about patients from healthcare providers"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='notes')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_notes')
    note = models.TextField()
    is_private = models.BooleanField(default=True, help_text="Private notes only visible to providers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.patient.user.username} by {self.provider.username}"
