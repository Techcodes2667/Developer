# Developer Guide

This guide provides detailed information for developers working on the Telehealth Diabetes Care System.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Database Design](#database-design)
- [Frontend Development](#frontend-development)
- [Backend Development](#backend-development)
- [Testing](#testing)
- [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### System Architecture

The Telehealth Diabetes Care System follows a Model-View-Controller (MVC) architecture using Django framework:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│   (Templates)   │◄──►│   (Django)      │◄──►│  (PostgreSQL)   │
│   Bootstrap 5   │    │   Python 3.8+   │    │                 │
│   JavaScript    │    │   Django 4.2+   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Backend:**
- **Framework**: Django 4.2+
- **Language**: Python 3.8+
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: Django's built-in auth system
- **API**: Django REST Framework (for API endpoints)

**Frontend:**
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with Chart.js for visualizations
- **Icons**: Font Awesome
- **Templates**: Django template engine

**Development Tools:**
- **Version Control**: Git
- **Package Management**: pip, requirements.txt
- **Testing**: Django's built-in testing framework
- **Code Quality**: flake8, black (optional)

## Development Setup

### Prerequisites

1. **Python 3.8+**
2. **PostgreSQL** (for production-like development)
3. **Git**
4. **Code Editor** (VS Code recommended)

### Environment Setup

1. **Clone Repository**
```bash
git clone https://github.com/Techcodes2667/Developer.git
cd My_tele_app/telehealth_diabetes
```

2. **Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Environment Variables**
Create `.env` file:
```env
SECRET_KEY=your-development-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/telehealth_dev
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Load Sample Data**
```bash
python manage.py populate_medications
python manage.py populate_education
python manage.py populate_support_groups
```

### Development Server

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`

## Code Structure

### Django Apps

The project is organized into Django apps, each handling specific functionality:

```
telehealth_diabetes/
├── main/                    # Public pages, homepage
├── accounts/               # User authentication
├── patients/               # Patient profiles and dashboard
├── health_data/           # Health metrics tracking
├── medication_management/ # Medication tracking
├── appointments/          # Appointment system
├── education/             # Educational content
├── mental_health/         # Mental wellness
├── support_groups/        # Community features
└── goals/                 # Goal setting and tracking
```

### App Structure

Each Django app follows this structure:

```
app_name/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py               # App configuration
├── models.py             # Database models
├── views.py              # View functions/classes
├── urls.py               # URL routing
├── forms.py              # Django forms (if needed)
├── serializers.py        # DRF serializers (if API)
├── tests.py              # Unit tests
├── migrations/           # Database migrations
├── management/           # Custom management commands
│   └── commands/
└── templates/            # App-specific templates
    └── app_name/
```

### Key Files

**Project Settings:**
- `settings.py`: Main configuration
- `urls.py`: Root URL configuration
- `wsgi.py`: WSGI application

**Static Files:**
- `static/css/`: Custom CSS files
- `static/js/`: JavaScript files
- `static/images/`: Image assets

**Templates:**
- `templates/base.html`: Base template
- `templates/includes/`: Reusable template components

## Database Design

### Core Models

#### Patient Profile
```python
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    diabetes_type = models.CharField(max_length=20)
    diagnosis_date = models.DateField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
```

#### Health Data Models
```python
class BloodGlucoseReading(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    value = models.FloatField()
    unit = models.CharField(max_length=10)
    reading_type = models.CharField(max_length=20)
    recorded_at = models.DateTimeField(auto_now_add=True)
```

#### Medication Models
```python
class PatientMedication(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
```

### Database Relationships

```
User (Django) ──1:1── PatientProfile
                         │
                         ├──1:N── BloodGlucoseReading
                         ├──1:N── PatientMedication
                         ├──1:N── Appointment
                         ├──1:N── HealthGoal
                         └──1:N── MoodEntry

Medication ──1:N── PatientMedication
Provider ──1:N── Appointment
SupportGroup ──N:M── PatientProfile (through GroupMembership)
```

### Migrations

**Creating Migrations:**
```bash
python manage.py makemigrations app_name
```

**Applying Migrations:**
```bash
python manage.py migrate
```

**Custom Migrations:**
```python
# migrations/0002_custom_data.py
from django.db import migrations

def populate_medications(apps, schema_editor):
    Medication = apps.get_model('medication_management', 'Medication')
    # Add custom data population logic

class Migration(migrations.Migration):
    dependencies = [
        ('medication_management', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(populate_medications),
    ]
```

## Frontend Development

### Template Structure

**Base Template (`templates/base.html`):**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Telehealth Diabetes Care{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="{% static 'css/style.css' %}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'includes/navbar.html' %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'includes/footer.html' %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### JavaScript Patterns

**AJAX Requests:**
```javascript
// static/js/health-data.js
function submitGlucoseReading(formData) {
    fetch('/health-data/glucose/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Reading added successfully');
            updateChart(data.reading);
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('An error occurred');
    });
}
```

**Chart.js Integration:**
```javascript
// static/js/charts.js
function createGlucoseChart(data) {
    const ctx = document.getElementById('glucoseChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Blood Glucose',
                data: data.values,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 70,
                    max: 200
                }
            }
        }
    });
}
```

### CSS Organization

**Custom Styles (`static/css/style.css`):**
```css
/* Variables */
:root {
    --primary-color: #0d6efd;
    --success-color: #198754;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #0dcaf0;
}

/* Utility Classes */
.bg-gradient-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
}

.card-hover {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card-hover:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Component Styles */
.health-metric-card {
    border-left: 4px solid var(--primary-color);
}

.glucose-reading {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
}

.glucose-normal { background-color: #d4edda; }
.glucose-high { background-color: #f8d7da; }
.glucose-low { background-color: #fff3cd; }
```

## Backend Development

### View Patterns

**Function-Based Views:**
```python
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

@login_required
def add_glucose_reading(request):
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            value = float(request.POST.get('value'))
            unit = request.POST.get('unit')
            reading_type = request.POST.get('reading_type')
            
            reading = BloodGlucoseReading.objects.create(
                patient=patient_profile,
                value=value,
                unit=unit,
                reading_type=reading_type
            )
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'reading': {
                        'id': reading.id,
                        'value': reading.value,
                        'recorded_at': reading.recorded_at.isoformat()
                    }
                })
            
            messages.success(request, 'Reading added successfully')
            return redirect('health_data:dashboard')
            
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'message': str(e)})
            
            messages.error(request, f'Error adding reading: {str(e)}')
    
    return render(request, 'health_data/add_reading.html')
```

**Class-Based Views:**
```python
# views.py
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

class GlucoseReadingListView(LoginRequiredMixin, ListView):
    model = BloodGlucoseReading
    template_name = 'health_data/glucose_list.html'
    context_object_name = 'readings'
    paginate_by = 20
    
    def get_queryset(self):
        return BloodGlucoseReading.objects.filter(
            patient=self.request.user.patientprofile
        ).order_by('-recorded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chart_data'] = self.get_chart_data()
        return context
    
    def get_chart_data(self):
        readings = self.get_queryset()[:30]
        return {
            'labels': [r.recorded_at.strftime('%m/%d') for r in readings],
            'values': [r.value for r in readings]
        }
```

### Model Patterns

**Custom Model Methods:**
```python
# models.py
class HealthGoal(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    target_value = models.FloatField()
    current_value = models.FloatField(default=0)
    target_date = models.DateField()
    
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)
    
    def days_remaining(self):
        from django.utils import timezone
        if self.target_date < timezone.now().date():
            return 0
        return (self.target_date - timezone.now().date()).days
    
    def is_overdue(self):
        from django.utils import timezone
        return self.target_date < timezone.now().date() and self.status == 'active'
```

**Custom Managers:**
```python
# models.py
class ActiveMedicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class PatientMedication(models.Model):
    # ... fields ...
    
    objects = models.Manager()  # Default manager
    active = ActiveMedicationManager()  # Custom manager
    
    class Meta:
        ordering = ['-created_at']
```

### API Development

**Django REST Framework Serializers:**
```python
# serializers.py
from rest_framework import serializers
from .models import BloodGlucoseReading

class BloodGlucoseReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodGlucoseReading
        fields = ['id', 'value', 'unit', 'reading_type', 'recorded_at', 'notes']
        read_only_fields = ['id', 'recorded_at']
    
    def validate_value(self, value):
        if value < 20 or value > 600:
            raise serializers.ValidationError("Glucose value must be between 20 and 600")
        return value
```

**API Views:**
```python
# api_views.py
from rest_framework import generics, permissions
from rest_framework.response import Response

class BloodGlucoseReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = BloodGlucoseReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BloodGlucoseReading.objects.filter(
            patient=self.request.user.patientprofile
        )
    
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patientprofile)
```

## Testing

### Unit Tests

**Model Tests:**
```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import PatientProfile, BloodGlucoseReading

class BloodGlucoseReadingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.patient = PatientProfile.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            diabetes_type='type2'
        )
    
    def test_create_glucose_reading(self):
        reading = BloodGlucoseReading.objects.create(
            patient=self.patient,
            value=120.5,
            unit='mg/dL',
            reading_type='fasting'
        )
        self.assertEqual(reading.value, 120.5)
        self.assertEqual(reading.patient, self.patient)
    
    def test_glucose_reading_str(self):
        reading = BloodGlucoseReading.objects.create(
            patient=self.patient,
            value=120.5,
            unit='mg/dL',
            reading_type='fasting'
        )
        expected = f"{self.patient.user.username} - 120.5 mg/dL (fasting)"
        self.assertEqual(str(reading), expected)
```

**View Tests:**
```python
# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class HealthDataViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.patient = PatientProfile.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            diabetes_type='type2'
        )
    
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('health_data:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_with_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('health_data:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Health Dashboard')
```

### Integration Tests

**API Tests:**
```python
# tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class GlucoseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.patient = PatientProfile.objects.create(
            user=self.user,
            date_of_birth='1990-01-01',
            diabetes_type='type2'
        )
    
    def test_create_glucose_reading(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'value': 125.0,
            'unit': 'mg/dL',
            'reading_type': 'fasting'
        }
        response = self.client.post('/api/glucose/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['value'], 125.0)
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test health_data

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Contributing Guidelines

### Code Style

**Python Code Style:**
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Maximum line length: 88 characters (Black formatter)

**Example:**
```python
def calculate_glucose_average(readings: list, days: int = 7) -> float:
    """
    Calculate average glucose reading for specified number of days.
    
    Args:
        readings: List of BloodGlucoseReading objects
        days: Number of days to include in calculation
    
    Returns:
        Average glucose value as float
    """
    if not readings:
        return 0.0
    
    recent_readings = readings[:days]
    total = sum(reading.value for reading in recent_readings)
    return total / len(recent_readings)
```

### Git Workflow

**Branch Naming:**
- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes
- `docs/documentation-update`: Documentation changes

**Commit Messages:**
```
feat: add blood glucose trend analysis

- Implement 30-day glucose trend calculation
- Add trend visualization to dashboard
- Include trend alerts for concerning patterns

Closes #123
```

**Pull Request Process:**
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation if needed
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

### Code Review Checklist

**Functionality:**
- [ ] Code works as expected
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

**Code Quality:**
- [ ] Code follows style guidelines
- [ ] Functions are well-documented
- [ ] Variable names are descriptive
- [ ] No code duplication

**Testing:**
- [ ] Unit tests are included
- [ ] Tests cover edge cases
- [ ] All tests pass
- [ ] Test coverage is adequate

**Security:**
- [ ] Input validation is present
- [ ] Authentication is required where needed
- [ ] No sensitive data in logs
- [ ] SQL injection prevention

### Development Tools

**Recommended VS Code Extensions:**
- Python
- Django
- GitLens
- Prettier
- ESLint
- Django Template

**Pre-commit Hooks:**
```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

---

**Questions?** Contact the development team at oongugucodes@gmail.com
