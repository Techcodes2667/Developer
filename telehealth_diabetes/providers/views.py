from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProviderProfile, ProviderPatientAssignment

@login_required
def provider_dashboard(request):
    """Provider dashboard"""
    try:
        provider_profile = request.user.providerprofile
        assigned_patients = provider_profile.patient_assignments.filter(is_active=True).count()
        upcoming_appointments = provider_profile.appointments.filter(
            status__in=['scheduled', 'confirmed']
        ).count()
    except:
        assigned_patients = upcoming_appointments = 0
        messages.info(request, 'Please complete your provider profile first.')

    return render(request, 'providers/dashboard.html', {
        'assigned_patients': assigned_patients,
        'upcoming_appointments': upcoming_appointments,
    })

@login_required
def patient_management(request):
    """Patient management"""
    try:
        provider_profile = request.user.providerprofile
        assignments = provider_profile.patient_assignments.filter(is_active=True)
    except:
        assignments = []

    return render(request, 'providers/patients.html', {
        'assignments': assignments
    })

@login_required
def patient_detail(request, patient_id):
    """Patient detail for providers"""
    try:
        provider_profile = request.user.providerprofile
        assignment = get_object_or_404(
            ProviderPatientAssignment,
            provider=provider_profile,
            patient_id=patient_id,
            is_active=True
        )
    except:
        messages.error(request, 'Patient not found or not assigned to you.')
        return redirect('providers:patients')

    return render(request, 'providers/patient_detail.html', {
        'assignment': assignment,
        'patient': assignment.patient
    })

@login_required
def schedule_management(request):
    """Schedule management"""
    return render(request, 'providers/schedule.html')

@login_required
def message_center(request):
    """Message center"""
    return render(request, 'providers/messages.html')

@login_required
def provider_profile(request):
    """Provider profile"""
    try:
        provider_profile = request.user.providerprofile
    except ProviderProfile.DoesNotExist:
        provider_profile = None

    if request.method == 'POST':
        messages.info(request, 'Provider profile update functionality will be implemented.')
        return redirect('providers:profile')

    return render(request, 'providers/profile.html', {
        'provider_profile': provider_profile
    })
