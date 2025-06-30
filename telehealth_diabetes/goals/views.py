from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from datetime import timedelta, datetime
from .models import HealthGoal, GoalTemplate, PatientAchievement, GoalProgress
from patients.models import PatientProfile

def goals_home(request):
    """Goals home page"""
    # Get featured goal templates
    featured_templates = GoalTemplate.objects.filter(is_active=True, is_featured=True)[:6]

    # Get user's goals if logged in
    user_goals = []
    if request.user.is_authenticated:
        try:
            patient_profile = request.user.patientprofile
            user_goals = patient_profile.goals.filter(status='active')[:3]
        except PatientProfile.DoesNotExist:
            pass

    context = {
        'featured_templates': featured_templates,
        'user_goals': user_goals,
    }

    return render(request, 'goals/home.html', context)

@login_required
def goals_dashboard(request):
    """Goals dashboard"""
    try:
        patient_profile = request.user.patientprofile

        # Get goals by status
        active_goals = patient_profile.goals.filter(status='active').order_by('-created_at')
        completed_goals = patient_profile.goals.filter(status='completed').order_by('-completed_at')[:5]
        paused_goals = patient_profile.goals.filter(status='paused').order_by('-created_at')

        # Calculate statistics
        total_goals = patient_profile.goals.count()
        completed_count = completed_goals.count()
        completion_rate = (completed_count / total_goals * 100) if total_goals > 0 else 0

        # Get recent progress updates
        recent_progress = GoalProgress.objects.filter(
            goal__patient=patient_profile
        ).order_by('-recorded_at')[:10]

        # Get goals due soon (within 7 days)
        seven_days_from_now = timezone.now().date() + timedelta(days=7)
        goals_due_soon = active_goals.filter(
            target_date__lte=seven_days_from_now,
            target_date__gte=timezone.now().date()
        )

        context = {
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'paused_goals': paused_goals,
            'total_goals': total_goals,
            'completed_count': completed_count,
            'completion_rate': completion_rate,
            'recent_progress': recent_progress,
            'goals_due_soon': goals_due_soon,
        }

    except PatientProfile.DoesNotExist:
        messages.info(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    return render(request, 'goals/dashboard.html', context)

@login_required
def goal_list(request):
    """List patient goals"""
    try:
        patient_profile = request.user.patientprofile

        # Filter options
        status_filter = request.GET.get('status', 'all')
        category_filter = request.GET.get('category', 'all')

        goals = patient_profile.goals.all()

        # Apply filters
        if status_filter != 'all':
            goals = goals.filter(status=status_filter)

        if category_filter != 'all':
            goals = goals.filter(category=category_filter)

        goals = goals.order_by('-created_at')

        # Pagination
        paginator = Paginator(goals, 10)
        page_number = request.GET.get('page')
        goals_page = paginator.get_page(page_number)

        context = {
            'goals': goals_page,
            'status_filter': status_filter,
            'category_filter': category_filter,
            'goal_categories': HealthGoal.CATEGORY_CHOICES,
            'goal_statuses': HealthGoal.STATUS_CHOICES,
        }

    except PatientProfile.DoesNotExist:
        messages.info(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    return render(request, 'goals/list.html', context)

@login_required
def create_goal(request):
    """Create new goal"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile

            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category')
            target_value = request.POST.get('target_value')
            target_unit = request.POST.get('target_unit', '')
            target_date = request.POST.get('target_date')
            template_id = request.POST.get('template_id')

            # Create goal from template or custom
            if template_id:
                template = get_object_or_404(GoalTemplate, id=template_id, is_active=True)
                goal = HealthGoal.objects.create(
                    patient=patient_profile,
                    title=template.title,
                    description=template.description,
                    category=template.category,
                    target_value=float(target_value) if target_value else template.default_target_value,
                    target_unit=template.target_unit,
                    target_date=datetime.strptime(target_date, '%Y-%m-%d').date(),
                    template=template
                )
            else:
                goal = HealthGoal.objects.create(
                    patient=patient_profile,
                    title=title,
                    description=description,
                    category=category,
                    target_value=float(target_value) if target_value else 0,
                    target_unit=target_unit,
                    target_date=datetime.strptime(target_date, '%Y-%m-%d').date()
                )

            messages.success(request, f'Goal "{goal.title}" created successfully!')
            return redirect('goals:detail', goal_id=goal.id)

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
            return redirect('patients:profile')
        except Exception as e:
            messages.error(request, f'Error creating goal: {str(e)}')

    templates = GoalTemplate.objects.filter(is_active=True)
    return render(request, 'goals/create.html', {
        'templates': templates,
        'goal_categories': HealthGoal.CATEGORY_CHOICES
    })

@login_required
def goal_detail(request, goal_id):
    """Goal detail view"""
    try:
        patient_profile = request.user.patientprofile
        goal = get_object_or_404(HealthGoal, id=goal_id, patient=patient_profile)

        # Get progress history
        progress_history = goal.progress_entries.order_by('-recorded_at')[:20]

        # Calculate progress statistics
        if progress_history:
            latest_progress = progress_history.first()
            avg_progress = progress_history.aggregate(avg=Avg('current_value'))['avg'] or 0
        else:
            latest_progress = None
            avg_progress = 0

        # Check if goal is overdue
        is_overdue = goal.target_date < timezone.now().date() and goal.status == 'active'

        # Days remaining
        days_remaining = (goal.target_date - timezone.now().date()).days if goal.status == 'active' else 0

        context = {
            'goal': goal,
            'progress_history': progress_history,
            'latest_progress': latest_progress,
            'avg_progress': round(avg_progress, 2),
            'is_overdue': is_overdue,
            'days_remaining': days_remaining,
        }

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')
    except HealthGoal.DoesNotExist:
        messages.error(request, 'Goal not found.')
        return redirect('goals:list')

    return render(request, 'goals/detail.html', context)

@login_required
def update_progress(request, goal_id):
    """Update goal progress"""
    try:
        patient_profile = request.user.patientprofile
        goal = get_object_or_404(HealthGoal, id=goal_id, patient=patient_profile)

        if goal.status != 'active':
            messages.error(request, 'Cannot update progress for inactive goals.')
            return redirect('goals:detail', goal_id=goal_id)

    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')
    except HealthGoal.DoesNotExist:
        messages.error(request, 'Goal not found.')
        return redirect('goals:list')

    if request.method == 'POST':
        current_value = request.POST.get('current_value')
        notes = request.POST.get('notes', '')

        try:
            # Create progress entry
            progress = GoalProgress.objects.create(
                goal=goal,
                current_value=float(current_value),
                notes=notes
            )

            # Update goal's current value
            goal.current_value = float(current_value)

            # Check if goal is completed
            if goal.target_value and float(current_value) >= goal.target_value:
                goal.status = 'completed'
                goal.completed_at = timezone.now()

                # Create achievement if goal completed
                PatientAchievement.objects.create(
                    patient=patient_profile,
                    title=f'Completed: {goal.title}',
                    description=f'Successfully achieved the goal "{goal.title}"',
                    achievement_type='goal_completion',
                    points_earned=goal.calculate_points()
                )

                messages.success(request, f'Congratulations! You completed your goal: {goal.title}')
            else:
                messages.success(request, 'Progress updated successfully!')

            goal.save()
            return redirect('goals:detail', goal_id=goal_id)

        except ValueError:
            messages.error(request, 'Please enter a valid number for progress.')
        except Exception as e:
            messages.error(request, f'Error updating progress: {str(e)}')

    return render(request, 'goals/update_progress.html', {'goal': goal})

@login_required
def pause_goal(request, goal_id):
    """Pause/resume a goal"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            goal = get_object_or_404(HealthGoal, id=goal_id, patient=patient_profile)

            if goal.status == 'active':
                goal.status = 'paused'
                messages.success(request, f'Goal "{goal.title}" has been paused.')
            elif goal.status == 'paused':
                goal.status = 'active'
                messages.success(request, f'Goal "{goal.title}" has been resumed.')

            goal.save()

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
        except HealthGoal.DoesNotExist:
            messages.error(request, 'Goal not found.')

    return redirect('goals:detail', goal_id=goal_id)

@login_required
def delete_goal(request, goal_id):
    """Delete a goal"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            goal = get_object_or_404(HealthGoal, id=goal_id, patient=patient_profile)

            goal_title = goal.title
            goal.delete()

            messages.success(request, f'Goal "{goal_title}" has been deleted.')

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Profile not found.')
        except HealthGoal.DoesNotExist:
            messages.error(request, 'Goal not found.')

    return redirect('goals:list')

@login_required
def quick_progress_update(request):
    """Quick progress update via AJAX"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            goal_id = request.POST.get('goal_id')
            current_value = request.POST.get('current_value')

            goal = get_object_or_404(HealthGoal, id=goal_id, patient=patient_profile)

            if goal.status != 'active':
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot update progress for inactive goals'
                })

            # Create progress entry
            GoalProgress.objects.create(
                goal=goal,
                current_value=float(current_value),
                notes='Quick update'
            )

            # Update goal
            goal.current_value = float(current_value)

            # Check completion
            if goal.target_value and float(current_value) >= goal.target_value:
                goal.status = 'completed'
                goal.completed_at = timezone.now()

                # Create achievement
                PatientAchievement.objects.create(
                    patient=patient_profile,
                    title=f'Completed: {goal.title}',
                    description=f'Successfully achieved the goal "{goal.title}"',
                    achievement_type='goal_completion',
                    points_earned=goal.calculate_points()
                )

            goal.save()

            return JsonResponse({
                'success': True,
                'message': 'Progress updated successfully',
                'completed': goal.status == 'completed'
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

@login_required
def achievements(request):
    """Patient achievements"""
    try:
        patient_profile = request.user.patientprofile
        achievements = patient_profile.achievements.all()
    except:
        achievements = []

    return render(request, 'goals/achievements.html', {'achievements': achievements})

@login_required
def goal_templates(request):
    """Goal templates"""
    templates = GoalTemplate.objects.filter(is_active=True)
    return render(request, 'goals/templates.html', {'templates': templates})
