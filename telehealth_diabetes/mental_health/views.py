from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import (
    MentalHealthResource, SelfAssessment, CopingStrategy,
    MoodEntry, PatientAssessmentResult
)
from patients.models import PatientProfile

def mental_health_home(request):
    """Mental health home page"""
    resources = MentalHealthResource.objects.filter(is_published=True)[:6]
    assessments = SelfAssessment.objects.filter(is_active=True)[:3]
    strategies = CopingStrategy.objects.filter(is_published=True)[:4]

    # Get user's recent mood if logged in
    recent_mood = None
    if request.user.is_authenticated:
        try:
            patient_profile = request.user.patientprofile
            recent_mood = MoodEntry.objects.filter(patient=patient_profile).order_by('-recorded_at').first()
        except PatientProfile.DoesNotExist:
            pass

    context = {
        'resources': resources,
        'assessments': assessments,
        'strategies': strategies,
        'recent_mood': recent_mood,
    }

    return render(request, 'mental_health/home.html', context)

def resource_list(request):
    """Mental health resources"""
    resources = MentalHealthResource.objects.filter(is_published=True)
    topic = request.GET.get('topic')
    if topic:
        resources = resources.filter(topic=topic)

    return render(request, 'mental_health/resources.html', {
        'resources': resources,
        'selected_topic': topic
    })

def assessment_list(request):
    """Self-assessment tools"""
    assessments = SelfAssessment.objects.filter(is_active=True)
    return render(request, 'mental_health/assessments.html', {
        'assessments': assessments
    })

@login_required
def take_assessment(request, assessment_id):
    """Take self-assessment"""
    assessment = get_object_or_404(SelfAssessment, id=assessment_id, is_active=True)

    if request.method == 'POST':
        messages.info(request, 'Assessment functionality will be implemented.')
        return redirect('mental_health:assessments')

    return render(request, 'mental_health/take_assessment.html', {
        'assessment': assessment
    })

@login_required
def mood_tracking(request):
    """Mood tracking"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            mood_level = int(request.POST.get('mood_level'))
            energy_level = int(request.POST.get('energy_level'))
            stress_level = int(request.POST.get('stress_level'))
            notes = request.POST.get('notes', '')

            MoodEntry.objects.create(
                patient=patient_profile,
                mood_level=mood_level,
                energy_level=energy_level,
                stress_level=stress_level,
                notes=notes
            )

            messages.success(request, 'Mood entry recorded successfully!')
            return redirect('mental_health:mood_tracking')

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
            return redirect('patients:profile')
        except Exception as e:
            messages.error(request, f'Error recording mood: {str(e)}')

    try:
        patient_profile = request.user.patientprofile

        # Get recent mood entries
        recent_moods = patient_profile.mood_entries.order_by('-recorded_at')[:30]

        # Calculate averages for the last 7 days
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        recent_week_moods = patient_profile.mood_entries.filter(recorded_at__gte=seven_days_ago)

        avg_mood = recent_week_moods.aggregate(avg=Avg('mood_level'))['avg'] or 0
        avg_energy = recent_week_moods.aggregate(avg=Avg('energy_level'))['avg'] or 0
        avg_stress = recent_week_moods.aggregate(avg=Avg('stress_level'))['avg'] or 0

    except PatientProfile.DoesNotExist:
        recent_moods = []
        avg_mood = avg_energy = avg_stress = 0
        messages.info(request, 'Please complete your profile first.')

    context = {
        'recent_moods': recent_moods,
        'avg_mood': round(avg_mood, 1),
        'avg_energy': round(avg_energy, 1),
        'avg_stress': round(avg_stress, 1),
    }

    return render(request, 'mental_health/mood_tracking.html', context)

def coping_strategies(request):
    """Coping strategies"""
    strategies = CopingStrategy.objects.filter(is_published=True)
    strategy_type = request.GET.get('type')
    if strategy_type:
        strategies = strategies.filter(strategy_type=strategy_type)

    return render(request, 'mental_health/coping_strategies.html', {
        'strategies': strategies,
        'selected_type': strategy_type
    })

@login_required
def assessment_results(request):
    """View assessment results"""
    try:
        patient_profile = request.user.patientprofile
        results = PatientAssessmentResult.objects.filter(patient=patient_profile).order_by('-taken_at')

        # Pagination
        paginator = Paginator(results, 10)
        page_number = request.GET.get('page')
        results_page = paginator.get_page(page_number)

    except PatientProfile.DoesNotExist:
        results_page = []
        messages.info(request, 'Please complete your profile first.')

    return render(request, 'mental_health/assessment_results.html', {
        'results': results_page
    })

@login_required
def wellness_dashboard(request):
    """Mental wellness dashboard"""
    try:
        patient_profile = request.user.patientprofile

        # Get recent mood trends
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        mood_entries = patient_profile.mood_entries.filter(recorded_at__gte=thirty_days_ago)

        # Calculate wellness metrics
        total_entries = mood_entries.count()
        avg_mood = mood_entries.aggregate(avg=Avg('mood_level'))['avg'] or 0
        avg_energy = mood_entries.aggregate(avg=Avg('energy_level'))['avg'] or 0
        avg_stress = mood_entries.aggregate(avg=Avg('stress_level'))['avg'] or 0

        # Get recent assessments
        recent_assessments = PatientAssessmentResult.objects.filter(
            patient=patient_profile
        ).order_by('-taken_at')[:3]

        # Wellness score calculation (simple algorithm)
        wellness_score = 0
        if total_entries > 0:
            mood_score = (avg_mood / 5) * 40  # 40% weight
            energy_score = (avg_energy / 5) * 30  # 30% weight
            stress_score = ((5 - avg_stress) / 5) * 30  # 30% weight (inverted)
            wellness_score = mood_score + energy_score + stress_score

        context = {
            'total_entries': total_entries,
            'avg_mood': round(avg_mood, 1),
            'avg_energy': round(avg_energy, 1),
            'avg_stress': round(avg_stress, 1),
            'wellness_score': round(wellness_score, 1),
            'recent_assessments': recent_assessments,
            'mood_entries': mood_entries[:7],  # Last 7 entries for chart
        }

    except PatientProfile.DoesNotExist:
        context = {
            'total_entries': 0,
            'avg_mood': 0,
            'avg_energy': 0,
            'avg_stress': 0,
            'wellness_score': 0,
            'recent_assessments': [],
            'mood_entries': [],
        }
        messages.info(request, 'Please complete your profile first.')

    return render(request, 'mental_health/wellness_dashboard.html', context)

@login_required
def quick_mood_check(request):
    """Quick mood check via AJAX"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            mood_level = int(request.POST.get('mood_level'))

            MoodEntry.objects.create(
                patient=patient_profile,
                mood_level=mood_level,
                energy_level=mood_level,  # Default to same as mood
                stress_level=5 - mood_level,  # Inverse relationship
                notes='Quick mood check'
            )

            return JsonResponse({
                'success': True,
                'message': 'Mood recorded successfully'
            })

        except PatientProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Profile not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def crisis_resources(request):
    """Crisis and emergency mental health resources"""
    crisis_resources = [
        {
            'name': 'Kenya National Suicide Prevention Hotline',
            'phone': '0800 720 000',
            'description': '24/7 crisis support and suicide prevention',
            'availability': '24/7'
        },
        {
            'name': 'Befrienders Kenya',
            'phone': '0722 178 177',
            'description': 'Emotional support and crisis intervention',
            'availability': '24/7'
        },
        {
            'name': 'Kenya Red Cross Psychosocial Support',
            'phone': '0700 395 395',
            'description': 'Psychosocial support and counseling',
            'availability': 'Business hours'
        },
        {
            'name': 'Kisumu County Mental Health Services',
            'phone': '057 202 3000',
            'description': 'Local mental health services and referrals',
            'availability': 'Business hours'
        }
    ]

    warning_signs = [
        'Thoughts of self-harm or suicide',
        'Severe depression or hopelessness',
        'Panic attacks or severe anxiety',
        'Substance abuse',
        'Inability to care for yourself',
        'Hearing voices or seeing things',
        'Extreme mood swings'
    ]

    return render(request, 'mental_health/crisis_resources.html', {
        'crisis_resources': crisis_resources,
        'warning_signs': warning_signs
    })
