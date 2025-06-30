from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def health_data_home(request):
    """Health data dashboard"""
    try:
        patient_profile = request.user.patientprofile
        recent_glucose = patient_profile.glucose_readings.first()
        recent_weight = patient_profile.weight_readings.first()
        recent_activity = patient_profile.activity_records.first()
    except:
        recent_glucose = recent_weight = recent_activity = None
        messages.info(request, 'Please complete your profile first.')

    return render(request, 'health_data/home.html', {
        'recent_glucose': recent_glucose,
        'recent_weight': recent_weight,
        'recent_activity': recent_activity,
    })

@login_required
def glucose_tracking(request):
    """Blood glucose tracking"""
    return render(request, 'health_data/glucose.html')

@login_required
def weight_tracking(request):
    """Weight tracking"""
    return render(request, 'health_data/weight.html')

@login_required
def activity_tracking(request):
    """Activity tracking"""
    return render(request, 'health_data/activity.html')

@login_required
def health_reports(request):
    """Health reports"""
    return render(request, 'health_data/reports.html')
