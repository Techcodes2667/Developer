from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import PatientProfile

class GoalCategory(models.Model):
    """Categories for health goals"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")

    class Meta:
        verbose_name_plural = "Goal Categories"

    def __str__(self):
        return self.name

class HealthGoal(models.Model):
    """Patient health goals"""
    GOAL_TYPES = [
        ('blood_glucose', 'Blood Glucose Management'),
        ('weight', 'Weight Management'),
        ('exercise', 'Exercise & Activity'),
        ('medication', 'Medication Adherence'),
        ('diet', 'Diet & Nutrition'),
        ('sleep', 'Sleep Quality'),
        ('stress', 'Stress Management'),
        ('education', 'Diabetes Education'),
        ('custom', 'Custom Goal'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='goals')
    category = models.ForeignKey(GoalCategory, on_delete=models.SET_NULL, null=True, blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)

    # Goal details
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_value = models.FloatField(null=True, blank=True, help_text="Numeric target if applicable")
    target_unit = models.CharField(max_length=20, blank=True, help_text="e.g., kg, mmol/L, minutes")
    current_value = models.FloatField(null=True, blank=True)

    # Timeline
    start_date = models.DateField()
    target_date = models.DateField()

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Motivation
    motivation = models.TextField(blank=True, help_text="Why this goal is important")
    reward = models.CharField(max_length=200, blank=True, help_text="Reward for achieving goal")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.title}"

    @property
    def is_overdue(self):
        return self.target_date < timezone.now().date() and self.status == 'active'

    @property
    def days_remaining(self):
        if self.status == 'active':
            delta = self.target_date - timezone.now().date()
            return delta.days
        return None

    def update_progress(self, new_value=None, percentage=None):
        """Update goal progress"""
        if percentage is not None:
            self.progress_percentage = min(100, max(0, percentage))
        elif new_value is not None and self.target_value:
            # Calculate percentage based on current vs target value
            if self.goal_type in ['weight', 'blood_glucose']:
                # For these goals, closer to target is better
                if self.current_value:
                    improvement = abs(self.current_value - new_value)
                    total_needed = abs(self.current_value - self.target_value)
                    if total_needed > 0:
                        self.progress_percentage = min(100, int((improvement / total_needed) * 100))
            else:
                # For exercise, education etc., more is better
                self.progress_percentage = min(100, int((new_value / self.target_value) * 100))

            self.current_value = new_value

        if self.progress_percentage >= 100 and self.status == 'active':
            self.status = 'completed'
            self.completed_at = timezone.now()

        self.save()

class GoalMilestone(models.Model):
    """Milestones for tracking goal progress"""
    goal = models.ForeignKey(HealthGoal, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.FloatField(null=True, blank=True)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return f"{self.goal.title} - {self.title}"

class GoalProgress(models.Model):
    """Daily/weekly progress entries for goals"""
    goal = models.ForeignKey(HealthGoal, on_delete=models.CASCADE, related_name='progress_entries')
    date = models.DateField()
    value = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    mood = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('okay', 'Okay'),
        ('difficult', 'Difficult'),
        ('struggling', 'Struggling'),
    ], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['goal', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.goal.title} - {self.date}"

class Achievement(models.Model):
    """Achievements and badges for gamification"""
    ACHIEVEMENT_TYPES = [
        ('goal_completion', 'Goal Completion'),
        ('streak', 'Streak Achievement'),
        ('milestone', 'Milestone Achievement'),
        ('participation', 'Participation'),
        ('improvement', 'Improvement'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=50, blank=True)
    badge_color = models.CharField(max_length=7, default='#ffd700')
    points = models.IntegerField(default=10)

    # Criteria
    criteria_description = models.TextField(help_text="What needs to be done to earn this")
    is_repeatable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PatientAchievement(models.Model):
    """Achievements earned by patients"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    related_goal = models.ForeignKey(HealthGoal, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['patient', 'achievement', 'related_goal']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.patient.user.username} earned {self.achievement.name}"

class GoalTemplate(models.Model):
    """Pre-defined goal templates for common diabetes goals"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=HealthGoal.GOAL_TYPES)
    default_target_value = models.FloatField(null=True, blank=True)
    default_target_unit = models.CharField(max_length=20, blank=True)
    default_duration_days = models.IntegerField(default=30)
    tips = models.TextField(blank=True, help_text="Tips for achieving this goal")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
