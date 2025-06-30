from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import PatientProfile

class MentalHealthResource(models.Model):
    """Mental health resources and articles"""
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio/Meditation'),
        ('exercise', 'Exercise/Technique'),
        ('assessment', 'Self-Assessment'),
        ('external_link', 'External Resource'),
    ]

    TOPICS = [
        ('stress', 'Stress Management'),
        ('anxiety', 'Anxiety'),
        ('depression', 'Depression'),
        ('coping', 'Coping Strategies'),
        ('mindfulness', 'Mindfulness'),
        ('sleep', 'Sleep Issues'),
        ('relationships', 'Relationships'),
        ('diabetes_distress', 'Diabetes Distress'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    topic = models.CharField(max_length=30, choices=TOPICS)
    content = models.TextField(blank=True)
    external_url = models.URLField(blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)

    # Targeting
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mental_health_resources')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class SelfAssessment(models.Model):
    """Mental health self-assessment tools"""
    ASSESSMENT_TYPES = [
        ('phq9', 'PHQ-9 (Depression)'),
        ('gad7', 'GAD-7 (Anxiety)'),
        ('stress', 'Stress Level'),
        ('diabetes_distress', 'Diabetes Distress'),
        ('sleep_quality', 'Sleep Quality'),
        ('custom', 'Custom Assessment'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    assessment_type = models.CharField(max_length=30, choices=ASSESSMENT_TYPES)
    instructions = models.TextField()
    disclaimer = models.TextField(default="This is not a diagnostic tool. Please consult a healthcare professional for proper evaluation.")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class AssessmentQuestion(models.Model):
    """Questions for self-assessments"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('scale', 'Rating Scale'),
        ('yes_no', 'Yes/No'),
        ('text', 'Text Response'),
    ]

    assessment = models.ForeignKey(SelfAssessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField()
    is_required = models.BooleanField(default=True)

    # For scale questions
    scale_min = models.IntegerField(null=True, blank=True)
    scale_max = models.IntegerField(null=True, blank=True)
    scale_min_label = models.CharField(max_length=100, blank=True)
    scale_max_label = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.assessment.name} - Q{self.order}"

class AssessmentChoice(models.Model):
    """Multiple choice options for assessment questions"""
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    score_value = models.IntegerField(default=0)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question.assessment.name} - {self.choice_text}"

class PatientAssessmentResult(models.Model):
    """Results of patient self-assessments"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='assessment_results')
    assessment = models.ForeignKey(SelfAssessment, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    max_possible_score = models.IntegerField()
    interpretation = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.assessment.name} ({self.total_score})"

    @property
    def score_percentage(self):
        if self.max_possible_score > 0:
            return round((self.total_score / self.max_possible_score) * 100, 1)
        return 0

class AssessmentResponse(models.Model):
    """Individual responses to assessment questions"""
    result = models.ForeignKey(PatientAssessmentResult, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    choice = models.ForeignKey(AssessmentChoice, on_delete=models.CASCADE, null=True, blank=True)
    scale_value = models.IntegerField(null=True, blank=True)
    text_response = models.TextField(blank=True)

    def __str__(self):
        return f"Response to {self.question}"

class MoodEntry(models.Model):
    """Daily mood tracking"""
    MOOD_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Very Good'),
    ]

    ENERGY_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Moderate'),
        (4, 'High'),
        (5, 'Very High'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='mood_entries')
    date = models.DateField()
    mood_rating = models.IntegerField(choices=MOOD_CHOICES)
    energy_level = models.IntegerField(choices=ENERGY_CHOICES)
    stress_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1 = No stress, 10 = Extremely stressed"
    )
    sleep_quality = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="1 = Very poor, 5 = Excellent"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['patient', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.patient.user.username} - {self.date} (Mood: {self.mood_rating})"

class CopingStrategy(models.Model):
    """Coping strategies for managing diabetes-related stress"""
    STRATEGY_TYPES = [
        ('breathing', 'Breathing Exercise'),
        ('meditation', 'Meditation'),
        ('physical', 'Physical Activity'),
        ('cognitive', 'Cognitive Technique'),
        ('social', 'Social Support'),
        ('creative', 'Creative Activity'),
        ('relaxation', 'Relaxation Technique'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    strategy_type = models.CharField(max_length=20, choices=STRATEGY_TYPES)
    instructions = models.TextField()
    duration_minutes = models.IntegerField(null=True, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    ], default='easy')

    # When to use
    best_for = models.CharField(max_length=200, blank=True, help_text="e.g., 'acute stress', 'before medical appointments'")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coping_strategies')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PatientCopingLog(models.Model):
    """Log of coping strategies used by patients"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='coping_logs')
    strategy = models.ForeignKey(CopingStrategy, on_delete=models.CASCADE)
    used_at = models.DateTimeField()
    effectiveness_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="1 = Not helpful, 5 = Very helpful"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.patient.user.username} used {self.strategy.title}"
