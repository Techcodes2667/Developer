from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from .models import (
    EducationContent, EducationCategory, Recipe, ExerciseRoutine,
    PatientProgress
)
from patients.models import PatientProfile

def education_home(request):
    """Education home page"""
    categories = EducationCategory.objects.filter(is_active=True).annotate(
        content_count=Count('content', filter=Q(content__is_published=True))
    )
    featured_content = EducationContent.objects.filter(is_published=True, is_featured=True)[:6]

    # Get recent content
    recent_content = EducationContent.objects.filter(is_published=True).order_by('-created_at')[:4]

    # Get popular content
    popular_content = EducationContent.objects.filter(is_published=True).order_by('-view_count')[:4]

    # Get user progress if logged in
    user_progress = []
    if request.user.is_authenticated:
        try:
            patient_profile = request.user.patientprofile
            user_progress = PatientProgress.objects.filter(
                patient=patient_profile,
                progress_percentage__lt=100
            ).order_by('-started_at')[:3]
        except PatientProfile.DoesNotExist:
            pass

    context = {
        'categories': categories,
        'featured_content': featured_content,
        'recent_content': recent_content,
        'popular_content': popular_content,
        'user_progress': user_progress,
    }

    return render(request, 'education/home.html', context)

def content_library(request):
    """Education content library"""
    content_list = EducationContent.objects.filter(is_published=True).order_by('-created_at')
    categories = EducationCategory.objects.filter(is_active=True)

    # Filter by category if specified
    category_id = request.GET.get('category')
    selected_category_obj = None
    if category_id:
        try:
            selected_category_obj = EducationCategory.objects.get(id=category_id, is_active=True)
            content_list = content_list.filter(category=selected_category_obj)
        except EducationCategory.DoesNotExist:
            pass

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        content_list = content_list.filter(title__icontains=search_query)

    paginator = Paginator(content_list, 12)
    page_number = request.GET.get('page')
    content = paginator.get_page(page_number)

    return render(request, 'education/library.html', {
        'content': content,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_category_obj': selected_category_obj
    })

def content_detail(request, slug):
    """Education content detail"""
    content = get_object_or_404(EducationContent, slug=slug, is_published=True)
    content.increment_view_count()

    # Track progress if user is logged in
    progress = None
    related_content = []

    if request.user.is_authenticated:
        try:
            patient_profile = request.user.patientprofile
            progress, created = PatientProgress.objects.get_or_create(
                patient=patient_profile,
                content=content
            )
            if created:
                progress.started_at = timezone.now()
                progress.save()

            # Handle progress updates
            if request.method == 'POST':
                action = request.POST.get('action')
                if action == 'mark_complete':
                    progress.progress_percentage = 100
                    progress.completed_at = timezone.now()
                    progress.save()
                    messages.success(request, 'Content marked as completed!')
                    return redirect('education:content_detail', slug=slug)
                elif action == 'update_progress':
                    new_progress = int(request.POST.get('progress', 0))
                    progress.progress_percentage = min(100, max(0, new_progress))
                    if progress.progress_percentage == 100 and not progress.completed_at:
                        progress.completed_at = timezone.now()
                    progress.save()
                    return JsonResponse({'success': True, 'progress': progress.progress_percentage})
                elif action == 'rate_content':
                    rating = int(request.POST.get('rating', 0))
                    if 1 <= rating <= 5:
                        progress.rating = rating
                        progress.save()
                        messages.success(request, 'Thank you for your rating!')
                    return redirect('education:content_detail', slug=slug)
        except PatientProfile.DoesNotExist:
            pass

    # Get related content
    related_content = EducationContent.objects.filter(
        category=content.category,
        is_published=True
    ).exclude(id=content.id)[:4]

    # Get content in same difficulty level
    if not related_content.exists():
        related_content = EducationContent.objects.filter(
            difficulty_level=content.difficulty_level,
            is_published=True
        ).exclude(id=content.id)[:4]

    context = {
        'content': content,
        'progress': progress,
        'related_content': related_content,
    }

    return render(request, 'education/content_detail.html', context)

def recipe_list(request):
    """Recipe list"""
    recipes = Recipe.objects.filter(is_published=True).order_by('-created_at')

    # Filter by meal type
    meal_type = request.GET.get('meal_type')
    if meal_type:
        recipes = recipes.filter(meal_type=meal_type)

    paginator = Paginator(recipes, 12)
    page_number = request.GET.get('page')
    recipes_page = paginator.get_page(page_number)

    return render(request, 'education/recipes.html', {
        'recipes': recipes_page,
        'selected_meal_type': meal_type
    })

def recipe_detail(request, slug):
    """Recipe detail"""
    recipe = get_object_or_404(Recipe, slug=slug, is_published=True)

    return render(request, 'education/recipe_detail.html', {
        'recipe': recipe
    })

def exercise_list(request):
    """Exercise list"""
    exercises = ExerciseRoutine.objects.filter(is_published=True).order_by('-created_at')

    # Filter by intensity
    intensity = request.GET.get('intensity')
    if intensity:
        exercises = exercises.filter(intensity_level=intensity)

    paginator = Paginator(exercises, 12)
    page_number = request.GET.get('page')
    exercises_page = paginator.get_page(page_number)

    return render(request, 'education/exercises.html', {
        'exercises': exercises_page,
        'selected_intensity': intensity
    })

def exercise_detail(request, slug):
    """Exercise detail"""
    exercise = get_object_or_404(ExerciseRoutine, slug=slug, is_published=True)

    # Get related exercises
    related_exercises = ExerciseRoutine.objects.filter(
        intensity_level=exercise.intensity_level,
        is_published=True
    ).exclude(id=exercise.id)[:3]

    return render(request, 'education/exercise_detail.html', {
        'exercise': exercise,
        'related_exercises': related_exercises
    })

@login_required
def my_progress(request):
    """User's learning progress"""
    try:
        patient_profile = request.user.patientprofile

        # Get all progress
        all_progress = PatientProgress.objects.filter(patient=patient_profile)

        # Get completed content
        completed = all_progress.filter(progress_percentage=100).order_by('-completed_at')

        # Get in-progress content
        in_progress = all_progress.filter(
            progress_percentage__gt=0,
            progress_percentage__lt=100
        ).order_by('-started_at')

        # Get bookmarked content (started but not progressed)
        bookmarked = all_progress.filter(progress_percentage=0).order_by('-started_at')

        # Calculate statistics
        total_content = EducationContent.objects.filter(is_published=True).count()
        completed_count = completed.count()
        completion_rate = (completed_count / total_content * 100) if total_content > 0 else 0

        # Get average rating given by user
        avg_rating = all_progress.filter(rating__isnull=False).aggregate(
            avg=Avg('rating')
        )['avg'] or 0

        context = {
            'completed': completed,
            'in_progress': in_progress,
            'bookmarked': bookmarked,
            'total_content': total_content,
            'completed_count': completed_count,
            'completion_rate': completion_rate,
            'avg_rating': avg_rating,
        }

    except PatientProfile.DoesNotExist:
        messages.info(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    return render(request, 'education/my_progress.html', context)

@login_required
def bookmark_content(request, content_id):
    """Bookmark/unbookmark content"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            content = get_object_or_404(EducationContent, id=content_id, is_published=True)

            progress, created = PatientProgress.objects.get_or_create(
                patient=patient_profile,
                content=content
            )

            if created:
                messages.success(request, f'Added "{content.title}" to your learning list')
            else:
                messages.info(request, f'"{content.title}" is already in your learning list')

            return JsonResponse({'success': True, 'bookmarked': True})

        except PatientProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Profile not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

def search_content(request):
    """Search education content"""
    query = request.GET.get('q', '').strip()
    content_type = request.GET.get('type', 'all')
    difficulty = request.GET.get('difficulty', 'all')
    category_id = request.GET.get('category', 'all')

    # Start with published content
    results = EducationContent.objects.filter(is_published=True)

    # Apply search query
    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )

    # Apply filters
    if content_type != 'all':
        results = results.filter(content_type=content_type)

    if difficulty != 'all':
        results = results.filter(difficulty_level=difficulty)

    if category_id != 'all':
        results = results.filter(category_id=category_id)

    # Order by relevance (view count and featured status)
    results = results.order_by('-is_featured', '-view_count', '-created_at')

    # Pagination
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    search_results = paginator.get_page(page_number)

    # Get filter options
    categories = EducationCategory.objects.filter(is_active=True)
    content_types = EducationContent.CONTENT_TYPES
    difficulty_levels = EducationContent.DIFFICULTY_LEVELS

    context = {
        'search_results': search_results,
        'query': query,
        'content_type': content_type,
        'difficulty': difficulty,
        'category_id': category_id,
        'categories': categories,
        'content_types': content_types,
        'difficulty_levels': difficulty_levels,
        'total_results': results.count(),
    }

    return render(request, 'education/search.html', context)

def category_content(request, category_id):
    """Content by category"""
    category = get_object_or_404(EducationCategory, id=category_id, is_active=True)

    content_list = EducationContent.objects.filter(
        category=category,
        is_published=True
    ).order_by('-is_featured', '-created_at')

    # Pagination
    paginator = Paginator(content_list, 12)
    page_number = request.GET.get('page')
    content = paginator.get_page(page_number)

    return render(request, 'education/category.html', {
        'category': category,
        'content': content
    })
