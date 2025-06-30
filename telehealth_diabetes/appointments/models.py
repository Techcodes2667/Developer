from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from patients.models import PatientProfile

class HealthcareProvider(models.Model):
    """Healthcare providers who can conduct appointments"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, choices=[
        ('endocrinologist', 'Endocrinologist'),
        ('diabetes_educator', 'Diabetes Educator'),
        ('nutritionist', 'Nutritionist'),
        ('general_practitioner', 'General Practitioner'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
        ('mental_health', 'Mental Health Professional'),
    ])
    license_number = models.CharField(max_length=50, blank=True)
    years_experience = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.get_specialization_display()})"

class Appointment(models.Model):
    """Virtual appointments between patients and providers"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    APPOINTMENT_TYPES = [
        ('consultation', 'General Consultation'),
        ('follow_up', 'Follow-up'),
        ('education', 'Diabetes Education'),
        ('nutrition', 'Nutrition Counseling'),
        ('mental_health', 'Mental Health Support'),
        ('medication_review', 'Medication Review'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey(HealthcareProvider, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=30, choices=APPOINTMENT_TYPES)
    scheduled_datetime = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Pre-consultation information
    chief_complaint = models.TextField(blank=True, help_text="Patient's main concern")
    symptoms = models.TextField(blank=True)
    questions = models.TextField(blank=True)

    # Post-consultation information
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    next_appointment_recommended = models.BooleanField(default=False)

    # Technical details
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_datetime']

    def __str__(self):
        return f"{self.patient.user.username} with {self.provider.user.username} on {self.scheduled_datetime}"

    @property
    def is_upcoming(self):
        return self.scheduled_datetime > timezone.now() and self.status in ['scheduled', 'confirmed']

    @property
    def can_join(self):
        now = timezone.now()
        start_time = self.scheduled_datetime
        end_time = start_time + timezone.timedelta(minutes=self.duration_minutes)
        return start_time <= now <= end_time and self.status in ['scheduled', 'confirmed']

class AppointmentMessage(models.Model):
    """Messages between patient and provider related to appointments"""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.username} in appointment {self.appointment.id}"

class ProviderAvailability(models.Model):
    """Provider availability schedule"""
    provider = models.ForeignKey(HealthcareProvider, on_delete=models.CASCADE, related_name='availability')
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

    class Meta:
        unique_together = ['provider', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.provider.user.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class AppointmentFeedback(models.Model):
    """Feedback from patients about appointments"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="1-5 stars")
    comments = models.TextField(blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    technical_issues = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for appointment {self.appointment.id} - {self.rating} stars"
