from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from patients.models import PatientProfile

class ProviderProfile(models.Model):
    """Extended profile for healthcare providers"""
    SPECIALIZATIONS = [
        ('endocrinologist', 'Endocrinologist'),
        ('diabetes_educator', 'Diabetes Educator'),
        ('nutritionist', 'Nutritionist'),
        ('general_practitioner', 'General Practitioner'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
        ('mental_health', 'Mental Health Professional'),
        ('exercise_physiologist', 'Exercise Physiologist'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=30, choices=SPECIALIZATIONS)
    license_number = models.CharField(max_length=50, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)
    education = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    # Contact information
    phone_number = models.CharField(max_length=15, blank=True)
    office_address = models.TextField(blank=True)

    # Consultation details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    consultation_duration = models.IntegerField(default=30, help_text="Default consultation duration in minutes")

    # Availability
    is_accepting_patients = models.BooleanField(default=True)
    is_available_for_emergency = models.BooleanField(default=False)

    # Languages
    languages_spoken = models.CharField(max_length=200, blank=True, help_text="Comma-separated languages")

    # Ratings
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.get_specialization_display()})"

    def update_rating(self, new_rating):
        """Update provider's average rating"""
        total_score = self.average_rating * self.total_ratings + new_rating
        self.total_ratings += 1
        self.average_rating = total_score / self.total_ratings
        self.save()

class ProviderPatientAssignment(models.Model):
    """Assignment of patients to providers"""
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='patient_assignments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='provider_assignments')
    is_primary = models.BooleanField(default=False, help_text="Is this the patient's primary provider?")
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['provider', 'patient']

    def __str__(self):
        return f"{self.provider.user.username} assigned to {self.patient.user.username}"

class ProviderNote(models.Model):
    """Clinical notes by providers about patients"""
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='clinical_notes')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='provider_notes')
    note_type = models.CharField(max_length=30, choices=[
        ('consultation', 'Consultation Note'),
        ('assessment', 'Assessment'),
        ('treatment_plan', 'Treatment Plan'),
        ('follow_up', 'Follow-up'),
        ('medication_review', 'Medication Review'),
        ('general', 'General Note'),
    ])
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_shared_with_patient = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.patient.user.username}"

class ProviderMessage(models.Model):
    """Messages between providers and patients"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_provider_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_provider_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_urgent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}: {self.subject}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class ProviderSchedule(models.Model):
    """Provider working schedule"""
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ['provider', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.provider.user.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class ProviderTimeOff(models.Model):
    """Provider time off/unavailable periods"""
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='time_off')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.CharField(max_length=200, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.provider.user.username} unavailable {self.start_datetime} - {self.end_datetime}"

class ProviderRating(models.Model):
    """Patient ratings for providers"""
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='ratings')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='provider_ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="1-5 stars")
    review = models.TextField(blank=True)
    communication_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    knowledge_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    punctuality_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['provider', 'patient']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.user.username} rated {self.provider.user.username}: {self.rating} stars"
