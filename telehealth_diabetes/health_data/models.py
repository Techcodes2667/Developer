from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from patients.models import PatientProfile

class BloodGlucoseReading(models.Model):
    """Blood glucose measurements"""
    MEASUREMENT_TYPES = [
        ('fasting', 'Fasting'),
        ('before_meal', 'Before Meal'),
        ('after_meal', 'After Meal'),
        ('bedtime', 'Bedtime'),
        ('random', 'Random'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='glucose_readings')
    value = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(50.0)],
        help_text="Blood glucose in mmol/L"
    )
    measurement_type = models.CharField(max_length=20, choices=MEASUREMENT_TYPES)
    measured_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-measured_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.value} mmol/L ({self.get_measurement_type_display()})"

class WeightReading(models.Model):
    """Weight measurements"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='weight_readings')
    weight = models.FloatField(
        validators=[MinValueValidator(20.0), MaxValueValidator(500.0)],
        help_text="Weight in kg"
    )
    measured_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-measured_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.weight} kg"

class BloodPressureReading(models.Model):
    """Blood pressure measurements"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='bp_readings')
    systolic = models.IntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        help_text="Systolic pressure (mmHg)"
    )
    diastolic = models.IntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        help_text="Diastolic pressure (mmHg)"
    )
    measured_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-measured_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.systolic}/{self.diastolic} mmHg"

class CarbIntakeRecord(models.Model):
    """Carbohydrate intake tracking"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='carb_records')
    carbs_grams = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1000.0)],
        help_text="Carbohydrates in grams"
    )
    meal_type = models.CharField(max_length=20, choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ])
    food_description = models.TextField(blank=True)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.carbs_grams}g carbs ({self.get_meal_type_display()})"

class ActivityRecord(models.Model):
    """Physical activity tracking"""
    ACTIVITY_TYPES = [
        ('walking', 'Walking'),
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        ('swimming', 'Swimming'),
        ('gym', 'Gym Workout'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='activity_records')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(600)],
        help_text="Duration in minutes"
    )
    intensity = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ])
    description = models.TextField(blank=True)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.get_activity_type_display()} ({self.duration_minutes} min)"

class SleepRecord(models.Model):
    """Sleep pattern tracking"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='sleep_records')
    sleep_start = models.DateTimeField()
    sleep_end = models.DateTimeField()
    quality = models.CharField(max_length=10, choices=[
        ('poor', 'Poor'),
        ('fair', 'Fair'),
        ('good', 'Good'),
        ('excellent', 'Excellent'),
    ])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration_hours(self):
        if self.sleep_start and self.sleep_end:
            delta = self.sleep_end - self.sleep_start
            return round(delta.total_seconds() / 3600, 1)
        return None

    class Meta:
        ordering = ['-sleep_start']

    def __str__(self):
        return f"{self.patient.user.username} - {self.duration_hours}h sleep ({self.get_quality_display()})"
