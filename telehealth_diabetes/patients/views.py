from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import PatientProfile

@login_required
def profile(request):
    """Patient profile view"""
    try:
        patient_profile = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        patient_profile = None

    if request.method == 'POST':
        # Handle profile update
        if not patient_profile:
            patient_profile = PatientProfile.objects.create(user=request.user)

        # Update profile fields
        patient_profile.date_of_birth = request.POST.get('date_of_birth') or None
        patient_profile.gender = request.POST.get('gender', '')
        patient_profile.phone_number = request.POST.get('phone_number', '')
        patient_profile.address = request.POST.get('address', '')
        patient_profile.diabetes_type = request.POST.get('diabetes_type', '')
        patient_profile.diagnosis_date = request.POST.get('diagnosis_date') or None
        patient_profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('patients:profile')

    return render(request, 'patients/profile.html', {
        'patient_profile': patient_profile
    })

@login_required
def dashboard(request):
    """Patient dashboard view"""
    try:
        patient_profile = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        # Redirect to profile creation if no profile exists
        messages.info(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    # Get recent health data
    recent_glucose = patient_profile.glucose_readings.first()
    recent_weight = patient_profile.weight_readings.first()
    upcoming_appointments = patient_profile.appointments.filter(
        scheduled_datetime__gt=timezone.now(),
        status__in=['scheduled', 'confirmed']
    ).order_by('scheduled_datetime')[:3]

    # Get active medications
    active_medications = patient_profile.medications.filter(is_active=True)[:5]

    # Get active goals
    active_goals = patient_profile.goals.filter(status='active')[:3]

    context = {
        'patient_profile': patient_profile,
        'recent_glucose': recent_glucose,
        'recent_weight': recent_weight,
        'upcoming_appointments': upcoming_appointments,
        'active_medications': active_medications,
        'active_goals': active_goals,
    }

    return render(request, 'patients/dashboard.html', context)

@login_required
def monitoring(request):
    """Health monitoring view"""
    try:
        patient_profile = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        messages.info(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    # Get health data for charts
    glucose_readings = patient_profile.glucose_readings.order_by('-measured_at')[:30]
    weight_readings = patient_profile.weight_readings.order_by('-measured_at')[:30]

    context = {
        'patient_profile': patient_profile,
        'glucose_readings': glucose_readings,
        'weight_readings': weight_readings,
    }

    return render(request, 'patients/monitoring.html', context)

@login_required
def portal(request):
    """Patient portal main view"""
    return redirect('patients:dashboard')
