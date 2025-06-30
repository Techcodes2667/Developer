from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
from .models import (
    Medication, PatientMedication, MedicationLog,
    MedicationReminder, MedicationRefillRequest, DrugInteraction
)
from patients.models import PatientProfile

@login_required
def medication_list(request):
    """List patient medications"""
    try:
        patient_profile = request.user.patientprofile
        active_medications = patient_profile.medications.filter(is_active=True).order_by('medication__name')
        inactive_medications = patient_profile.medications.filter(is_active=False).order_by('-updated_at')[:5]

        # Get recent medication logs
        recent_logs = MedicationLog.objects.filter(
            patient_medication__patient=patient_profile
        ).order_by('-taken_at')[:10]

        # Get pending refill requests
        pending_refills = MedicationRefillRequest.objects.filter(
            patient_medication__patient=patient_profile,
            status='pending'
        ).order_by('-requested_at')

    except PatientProfile.DoesNotExist:
        active_medications = []
        inactive_medications = []
        recent_logs = []
        pending_refills = []
        messages.info(request, 'Please complete your profile first.')

    context = {
        'active_medications': active_medications,
        'inactive_medications': inactive_medications,
        'recent_logs': recent_logs,
        'pending_refills': pending_refills,
    }

    return render(request, 'medication_management/list.html', context)

@login_required
def add_medication(request):
    """Add new medication"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile

            # Get or create medication
            medication_name = request.POST.get('medication_name')
            medication, created = Medication.objects.get_or_create(
                name=medication_name,
                defaults={
                    'medication_type': request.POST.get('medication_type', 'other'),
                    'description': request.POST.get('description', '')
                }
            )

            # Create patient medication
            patient_medication = PatientMedication.objects.create(
                patient=patient_profile,
                medication=medication,
                dosage=request.POST.get('dosage'),
                frequency=request.POST.get('frequency'),
                instructions=request.POST.get('instructions', ''),
                prescribed_by=request.POST.get('prescribed_by', ''),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date') or None
            )

            # Create reminders if specified
            reminder_times = request.POST.getlist('reminder_times')
            for time_str in reminder_times:
                if time_str:
                    MedicationReminder.objects.create(
                        patient_medication=patient_medication,
                        reminder_time=time_str
                    )

            messages.success(request, f'Successfully added {medication.name} to your medications.')
            return redirect('medication_management:list')

        except Exception as e:
            messages.error(request, f'Error adding medication: {str(e)}')

    # Get available medications for autocomplete
    medications = Medication.objects.all().order_by('name')

    return render(request, 'medication_management/add.html', {
        'medications': medications
    })

@login_required
def medication_log(request):
    """Medication log"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            medication_id = request.POST.get('medication_id')
            patient_medication = get_object_or_404(
                PatientMedication,
                id=medication_id,
                patient=patient_profile,
                is_active=True
            )

            MedicationLog.objects.create(
                patient_medication=patient_medication,
                taken_at=timezone.now(),
                dosage_taken=request.POST.get('dosage_taken', patient_medication.dosage),
                notes=request.POST.get('notes', ''),
                was_reminder=request.POST.get('was_reminder') == 'on'
            )

            messages.success(request, f'Logged {patient_medication.medication.name}')
            return redirect('medication_management:log')

        except Exception as e:
            messages.error(request, f'Error logging medication: {str(e)}')

    try:
        patient_profile = request.user.patientprofile
        active_medications = patient_profile.medications.filter(is_active=True)

        # Get medication logs with pagination
        logs = MedicationLog.objects.filter(
            patient_medication__patient=patient_profile
        ).order_by('-taken_at')

        paginator = Paginator(logs, 20)
        page_number = request.GET.get('page')
        logs_page = paginator.get_page(page_number)

    except PatientProfile.DoesNotExist:
        active_medications = []
        logs_page = []

    return render(request, 'medication_management/log.html', {
        'active_medications': active_medications,
        'logs': logs_page
    })

@login_required
def reminders(request):
    """Medication reminders"""
    if request.method == 'POST':
        try:
            reminder_id = request.POST.get('reminder_id')
            action = request.POST.get('action')

            if action == 'toggle':
                reminder = get_object_or_404(MedicationReminder, id=reminder_id)
                reminder.is_active = not reminder.is_active
                reminder.save()
                status = 'enabled' if reminder.is_active else 'disabled'
                messages.success(request, f'Reminder {status}')

            elif action == 'add':
                medication_id = request.POST.get('medication_id')
                patient_medication = get_object_or_404(PatientMedication, id=medication_id)

                MedicationReminder.objects.create(
                    patient_medication=patient_medication,
                    reminder_time=request.POST.get('reminder_time'),
                    days_of_week=request.POST.get('days_of_week', '1234567')
                )
                messages.success(request, 'Reminder added successfully')

            return redirect('medication_management:reminders')

        except Exception as e:
            messages.error(request, f'Error managing reminder: {str(e)}')

    try:
        patient_profile = request.user.patientprofile
        active_medications = patient_profile.medications.filter(is_active=True)

        # Get all reminders for patient's medications
        reminders = MedicationReminder.objects.filter(
            patient_medication__patient=patient_profile
        ).order_by('reminder_time')

    except PatientProfile.DoesNotExist:
        active_medications = []
        reminders = []

    return render(request, 'medication_management/reminders.html', {
        'active_medications': active_medications,
        'reminders': reminders
    })

@login_required
def refill_requests(request):
    """Refill requests"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            medication_id = request.POST.get('medication_id')
            patient_medication = get_object_or_404(
                PatientMedication,
                id=medication_id,
                patient=patient_profile,
                is_active=True
            )

            # Create refill request
            MedicationRefillRequest.objects.create(
                patient_medication=patient_medication,
                pharmacy_name=request.POST.get('pharmacy_name', ''),
                pharmacy_phone=request.POST.get('pharmacy_phone', ''),
                quantity_requested=request.POST.get('quantity_requested'),
                notes=request.POST.get('notes', '')
            )

            messages.success(request, f'Refill request submitted for {patient_medication.medication.name}')
            return redirect('medication_management:refills')

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
        except Exception as e:
            messages.error(request, f'Error submitting refill request: {str(e)}')

    try:
        patient_profile = request.user.patientprofile
        active_medications = patient_profile.medications.filter(is_active=True)

        # Get refill requests with pagination
        refill_requests_list = MedicationRefillRequest.objects.filter(
            patient_medication__patient=patient_profile
        ).order_by('-requested_at')

        paginator = Paginator(refill_requests_list, 10)
        page_number = request.GET.get('page')
        refills_page = paginator.get_page(page_number)

    except PatientProfile.DoesNotExist:
        active_medications = []
        refills_page = []

    return render(request, 'medication_management/refills.html', {
        'active_medications': active_medications,
        'refill_requests': refills_page
    })

@login_required
def check_interactions(request):
    """Check drug interactions"""
    interactions = []

    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            selected_medications = request.POST.getlist('medications')

            if len(selected_medications) >= 2:
                # Check for interactions between selected medications
                for i, med1_id in enumerate(selected_medications):
                    for med2_id in selected_medications[i+1:]:
                        try:
                            med1 = Medication.objects.get(id=med1_id)
                            med2 = Medication.objects.get(id=med2_id)

                            # Check both directions of interaction
                            interaction = DrugInteraction.objects.filter(
                                medication1=med1, medication2=med2
                            ).first() or DrugInteraction.objects.filter(
                                medication1=med2, medication2=med1
                            ).first()

                            if interaction:
                                interactions.append({
                                    'medication1': med1,
                                    'medication2': med2,
                                    'interaction': interaction
                                })
                        except Medication.DoesNotExist:
                            continue

                if not interactions:
                    messages.success(request, 'No known interactions found between selected medications.')
                else:
                    messages.warning(request, f'Found {len(interactions)} potential interaction(s). Please review below.')
            else:
                messages.info(request, 'Please select at least 2 medications to check for interactions.')

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
        except Exception as e:
            messages.error(request, f'Error checking interactions: {str(e)}')

    try:
        patient_profile = request.user.patientprofile
        patient_medications = patient_profile.medications.filter(is_active=True)
    except PatientProfile.DoesNotExist:
        patient_medications = []

    # Get all available medications for manual checking
    all_medications = Medication.objects.all().order_by('name')

    return render(request, 'medication_management/interactions.html', {
        'patient_medications': patient_medications,
        'all_medications': all_medications,
        'interactions': interactions
    })

@login_required
def medication_detail(request, medication_id):
    """Medication detail view"""
    try:
        patient_profile = request.user.patientprofile
        patient_medication = get_object_or_404(
            PatientMedication,
            id=medication_id,
            patient=patient_profile
        )

        # Get recent logs for this medication
        recent_logs = patient_medication.logs.order_by('-taken_at')[:10]

        # Get reminders for this medication
        reminders = patient_medication.reminders.all()

        # Calculate adherence rate (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        logs_count = patient_medication.logs.filter(taken_at__gte=thirty_days_ago).count()

        # Simple adherence calculation (assuming once daily for now)
        expected_doses = 30  # This would be calculated based on frequency
        adherence_rate = min(100, (logs_count / expected_doses) * 100) if expected_doses > 0 else 0

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('medication_management:list')

    return render(request, 'medication_management/detail.html', {
        'patient_medication': patient_medication,
        'recent_logs': recent_logs,
        'reminders': reminders,
        'adherence_rate': adherence_rate
    })

@login_required
def quick_log_medication(request):
    """Quick log medication via AJAX"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            medication_id = request.POST.get('medication_id')

            patient_medication = get_object_or_404(
                PatientMedication,
                id=medication_id,
                patient=patient_profile,
                is_active=True
            )

            MedicationLog.objects.create(
                patient_medication=patient_medication,
                taken_at=timezone.now(),
                dosage_taken=patient_medication.dosage,
                was_reminder=True
            )

            return JsonResponse({
                'success': True,
                'message': f'Logged {patient_medication.medication.name}'
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
