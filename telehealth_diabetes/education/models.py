from django.db import models
from django.contrib.auth.models import User
from patients.models import PatientProfile

class EducationCategory(models.Model):
    """Categories for educational content"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Education Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class EducationContent(models.Model):
    """Educational articles, videos, and resources"""
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('infographic', 'Infographic'),
        ('quiz', 'Quiz'),
        ('checklist', 'Checklist'),
        ('recipe', 'Recipe'),
        ('exercise', 'Exercise Routine'),
    ]

    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(EducationCategory, on_delete=models.CASCADE, related_name='content')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')

    # Content
    summary = models.TextField(help_text="Brief summary for listings")
    content = models.TextField(help_text="Main content (HTML allowed)")
    video_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='education/images/', blank=True)

    # Metadata
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_content')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    estimated_read_time = models.IntegerField(null=True, blank=True, help_text="Minutes")

    # Targeting
    diabetes_types = models.CharField(max_length=100, blank=True, help_text="Comma-separated: type1,type2,gestational")
    target_audience = models.CharField(max_length=100, blank=True, help_text="e.g., newly_diagnosed,experienced")

    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class PatientProgress(models.Model):
    """Track patient progress through educational content"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='education_progress')
    content = models.ForeignKey(EducationContent, on_delete=models.CASCADE, related_name='patient_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['patient', 'content']
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.patient.user.username} - {self.content.title} ({self.progress_percentage}%)"

    @property
    def is_completed(self):
        return self.completed_at is not None

class Recipe(models.Model):
    """Diabetes-friendly recipes"""
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('dessert', 'Dessert'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    ingredients = models.TextField(help_text="One ingredient per line")
    instructions = models.TextField(help_text="Step-by-step instructions")

    # Nutritional information
    servings = models.IntegerField()
    prep_time_minutes = models.IntegerField()
    cook_time_minutes = models.IntegerField()
    calories_per_serving = models.IntegerField(null=True, blank=True)
    carbs_per_serving = models.FloatField(null=True, blank=True, help_text="Grams")
    protein_per_serving = models.FloatField(null=True, blank=True, help_text="Grams")
    fat_per_serving = models.FloatField(null=True, blank=True, help_text="Grams")
    fiber_per_serving = models.FloatField(null=True, blank=True, help_text="Grams")

    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='easy')

    image = models.ImageField(upload_to='recipes/', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_time_minutes(self):
        return self.prep_time_minutes + self.cook_time_minutes

class ExerciseRoutine(models.Model):
    """Exercise routines for diabetes management"""
    INTENSITY_LEVELS = [
        ('low', 'Low Intensity'),
        ('moderate', 'Moderate Intensity'),
        ('high', 'High Intensity'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    instructions = models.TextField()
    duration_minutes = models.IntegerField()
    intensity_level = models.CharField(max_length=20, choices=INTENSITY_LEVELS)
    equipment_needed = models.TextField(blank=True)
    target_muscle_groups = models.CharField(max_length=200, blank=True)

    # Suitability
    suitable_for_beginners = models.BooleanField(default=True)
    requires_supervision = models.BooleanField(default=False)
    contraindications = models.TextField(blank=True, help_text="When not to do this exercise")

    video_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='exercises/', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_routines')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
