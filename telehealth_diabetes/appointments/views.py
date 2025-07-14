from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from .models import (
    Appointment, HealthcareProvider, ProviderAvailability,
    AppointmentMessage, AppointmentFeedback
)
from patients.models import PatientProfile

@login_required
def schedule(request):
    """Schedule new appointment"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            provider_id = request.POST.get('provider_id')
            appointment_type = request.POST.get('appointment_type')
            scheduled_datetime_str = request.POST.get('scheduled_datetime')
            chief_complaint = request.POST.get('chief_complaint', '')
            symptoms = request.POST.get('symptoms', '')
            questions = request.POST.get('questions', '')

            # Parse datetime
            scheduled_datetime = datetime.fromisoformat(scheduled_datetime_str.replace('Z', '+00:00'))

            # Get provider
            provider = get_object_or_404(HealthcareProvider, id=provider_id, is_available=True)

            # Check if time slot is available
            existing_appointment = Appointment.objects.filter(
                provider=provider,
                scheduled_datetime=scheduled_datetime,
                status__in=['scheduled', 'confirmed']
            ).exists()

            if existing_appointment:
                messages.error(request, 'This time slot is no longer available. Please choose another time.')
                return redirect('appointments:schedule')

            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient_profile,
                provider=provider,
                appointment_type=appointment_type,
                scheduled_datetime=scheduled_datetime,
                chief_complaint=chief_complaint,
                symptoms=symptoms,
                questions=questions,
                status='scheduled'
            )

            messages.success(request, f'Appointment scheduled with {provider.user.get_full_name()} for {scheduled_datetime.strftime("%B %d, %Y at %I:%M %p")}')
            return redirect('appointments:detail', appointment_id=appointment.id)

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
            return redirect('patients:profile')
        except Exception as e:
            messages.error(request, f'Error scheduling appointment: {str(e)}')

    # Get available providers
    providers = HealthcareProvider.objects.filter(is_available=True).select_related('user')

    # Get appointment types
    appointment_types = Appointment.APPOINTMENT_TYPES

    return render(request, 'appointments/schedule.html', {
        'providers': providers,
        'appointment_types': appointment_types
    })

@login_required
def appointment_list(request):
    """List patient appointments"""
    try:
        patient_profile = request.user.patientprofile

        # Filter appointments
        status_filter = request.GET.get('status', 'all')
        if status_filter == 'upcoming':
            appointments = patient_profile.appointments.filter(
                scheduled_datetime__gt=timezone.now(),
                status__in=['scheduled', 'confirmed']
            )
        elif status_filter == 'past':
            appointments = patient_profile.appointments.filter(
                Q(scheduled_datetime__lt=timezone.now()) | Q(status__in=['completed', 'cancelled'])
            )
        elif status_filter != 'all':
            appointments = patient_profile.appointments.filter(status=status_filter)
        else:
            appointments = patient_profile.appointments.all()

        appointments = appointments.order_by('-scheduled_datetime')

        # Pagination
        paginator = Paginator(appointments, 10)
        page_number = request.GET.get('page')
        appointments_page = paginator.get_page(page_number)

        # Get counts for different statuses
        upcoming_count = patient_profile.appointments.filter(
            scheduled_datetime__gt=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).count()

        past_count = patient_profile.appointments.filter(
            Q(scheduled_datetime__lt=timezone.now()) | Q(status__in=['completed', 'cancelled'])
        ).count()

    except PatientProfile.DoesNotExist:
        appointments_page = []
        upcoming_count = 0
        past_count = 0
        status_filter = request.GET.get('status', 'all')
        messages.info(request, 'Please complete your profile first.')

    return render(request, 'appointments/list.html', {
        'appointments': appointments_page,
        'status_filter': status_filter,
        'upcoming_count': upcoming_count,
        'past_count': past_count
    })

@login_required
def appointment_detail(request, appointment_id):
    """Appointment detail view"""
    try:
        patient_profile = request.user.patientprofile
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient_profile)

        # Handle message sending
        if request.method == 'POST' and 'send_message' in request.POST:
            message_content = request.POST.get('message')
            if message_content:
                AppointmentMessage.objects.create(
                    appointment=appointment,
                    sender=request.user,
                    message=message_content
                )
                messages.success(request, 'Message sent successfully')
                return redirect('appointments:detail', appointment_id=appointment_id)

        # Handle appointment cancellation
        if request.method == 'POST' and 'cancel_appointment' in request.POST:
            if appointment.status in ['scheduled', 'confirmed']:
                appointment.status = 'cancelled'
                appointment.save()
                messages.success(request, 'Appointment cancelled successfully')
                return redirect('appointments:list')

        # Get messages for this appointment
        appointment_messages = appointment.messages.order_by('sent_at')

        # Mark messages as read
        appointment_messages.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('appointments:list')

    return render(request, 'appointments/detail.html', {
        'appointment': appointment,
        'messages': appointment_messages
    })

@login_required
def get_provider_availability(request, provider_id):
    """Get provider availability for scheduling (AJAX)"""
    try:
        provider = get_object_or_404(HealthcareProvider, id=provider_id)
        date_str = request.GET.get('date')

        if not date_str:
            return JsonResponse({'error': 'Date parameter required'}, status=400)

        # Parse the date
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = selected_date.weekday()

        # Get provider's availability for this day
        availability = ProviderAvailability.objects.filter(
            provider=provider,
            day_of_week=day_of_week,
            is_available=True
        ).first()

        if not availability:
            return JsonResponse({'available_slots': []})

        # Generate time slots
        available_slots = []
        current_time = datetime.combine(selected_date, availability.start_time)
        end_time = datetime.combine(selected_date, availability.end_time)

        # Check for existing appointments
        existing_appointments = Appointment.objects.filter(
            provider=provider,
            scheduled_datetime__date=selected_date,
            status__in=['scheduled', 'confirmed']
        ).values_list('scheduled_datetime', flat=True)

        existing_times = [apt.time() for apt in existing_appointments]

        # Generate 30-minute slots
        while current_time < end_time:
            # Skip break time if exists
            if (availability.break_start and availability.break_end and
                availability.break_start <= current_time.time() < availability.break_end):
                current_time += timedelta(minutes=30)
                continue

            # Skip if slot is already booked
            if current_time.time() not in existing_times:
                # Only show future slots
                if datetime.combine(selected_date, current_time.time()) > timezone.now():
                    available_slots.append({
                        'time': current_time.strftime('%H:%M'),
                        'display': current_time.strftime('%I:%M %p'),
                        'datetime': current_time.isoformat()
                    })

            current_time += timedelta(minutes=30)

        return JsonResponse({'available_slots': available_slots})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def join_appointment(request, appointment_id):
    """Join virtual appointment"""
    try:
        patient_profile = request.user.patientprofile
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=patient_profile
        )

        # Check if appointment can be joined
        if not appointment.can_join:
            messages.error(request, 'This appointment cannot be joined at this time.')
            return redirect('appointments:detail', appointment_id=appointment_id)

        # Update appointment status
        if appointment.status == 'confirmed':
            appointment.status = 'in_progress'
            appointment.save()

        # In a real implementation, this would redirect to a video call interface
        # For now, we'll show a placeholder page
        return render(request, 'appointments/join.html', {
            'appointment': appointment
        })

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('appointments:list')

@login_required
def appointment_feedback(request, appointment_id):
    """Submit appointment feedback"""
    try:
        patient_profile = request.user.patientprofile
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=patient_profile,
            status='completed'
        )

        # Check if feedback already exists
        existing_feedback = AppointmentFeedback.objects.filter(appointment=appointment).first()

        if request.method == 'POST':
            rating = request.POST.get('rating')
            comments = request.POST.get('comments', '')
            would_recommend = request.POST.get('would_recommend') == 'yes'
            technical_issues = request.POST.get('technical_issues') == 'yes'
            communication_rating = request.POST.get('communication_rating')
            knowledge_rating = request.POST.get('knowledge_rating')
            punctuality_rating = request.POST.get('punctuality_rating')

            if existing_feedback:
                # Update existing feedback
                existing_feedback.rating = rating
                existing_feedback.comments = comments
                existing_feedback.would_recommend = would_recommend
                existing_feedback.technical_issues = technical_issues
                existing_feedback.communication_rating = communication_rating
                existing_feedback.knowledge_rating = knowledge_rating
                existing_feedback.punctuality_rating = punctuality_rating
                existing_feedback.save()
                messages.success(request, 'Feedback updated successfully')
            else:
                # Create new feedback
                AppointmentFeedback.objects.create(
                    appointment=appointment,
                    rating=rating,
                    comments=comments,
                    would_recommend=would_recommend,
                    technical_issues=technical_issues,
                    communication_rating=communication_rating,
                    knowledge_rating=knowledge_rating,
                    punctuality_rating=punctuality_rating
                )
                messages.success(request, 'Thank you for your feedback!')

            return redirect('appointments:detail', appointment_id=appointment_id)

        return render(request, 'appointments/feedback.html', {
            'appointment': appointment,
            'existing_feedback': existing_feedback
        })

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found or not completed.')
        return redirect('appointments:list')

@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule an existing appointment"""
    try:
        patient_profile = request.user.patientprofile
        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=patient_profile,
            status__in=['scheduled', 'confirmed']
        )

        if request.method == 'POST':
            new_datetime_str = request.POST.get('new_datetime')
            new_datetime = datetime.fromisoformat(new_datetime_str.replace('Z', '+00:00'))

            # Check if new time slot is available
            existing_appointment = Appointment.objects.filter(
                provider=appointment.provider,
                scheduled_datetime=new_datetime,
                status__in=['scheduled', 'confirmed']
            ).exclude(id=appointment.id).exists()

            if existing_appointment:
                messages.error(request, 'This time slot is no longer available.')
                return redirect('appointments:reschedule', appointment_id=appointment_id)

            # Update appointment
            old_datetime = appointment.scheduled_datetime
            appointment.scheduled_datetime = new_datetime
            appointment.save()

            messages.success(request, f'Appointment rescheduled from {old_datetime.strftime("%B %d, %Y at %I:%M %p")} to {new_datetime.strftime("%B %d, %Y at %I:%M %p")}')
            return redirect('appointments:detail', appointment_id=appointment_id)

        return render(request, 'appointments/reschedule.html', {
            'appointment': appointment
        })

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found or cannot be rescheduled.')
        return redirect('appointments:list')
