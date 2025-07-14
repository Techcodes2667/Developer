from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from .models import (
    SupportGroup, GroupMembership, GroupDiscussion, GroupReply,
    LiveQASession, GroupMessage
)
from patients.models import PatientProfile

def support_groups_home(request):
    """Support groups home page"""
    # Get featured and popular groups
    featured_groups = SupportGroup.objects.filter(is_active=True, is_featured=True)[:3]
    popular_groups = SupportGroup.objects.filter(is_active=True).annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).order_by('-member_count')[:6]

    # Get recent activity if user is logged in
    user_groups = []
    recent_posts = []
    if request.user.is_authenticated:
        try:
            patient_profile = request.user.patientprofile
            user_groups = SupportGroup.objects.filter(
                memberships__patient=patient_profile,
                memberships__is_active=True
            )[:3]

            # Get recent posts from user's groups
            if user_groups:
                recent_posts = GroupDiscussion.objects.filter(
                    group__in=user_groups
                ).order_by('-created_at')[:5]
        except PatientProfile.DoesNotExist:
            pass

    context = {
        'featured_groups': featured_groups,
        'popular_groups': popular_groups,
        'user_groups': user_groups,
        'recent_posts': recent_posts,
    }

    return render(request, 'support_groups/home.html', context)

@login_required
def group_list(request):
    """List support groups"""
    # Filter options
    category = request.GET.get('category', 'all')
    search = request.GET.get('search', '')

    groups = SupportGroup.objects.filter(is_active=True).annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    )

    # Apply filters
    if category != 'all':
        groups = groups.filter(category=category)

    if search:
        groups = groups.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )

    # Order by member count and creation date
    groups = groups.order_by('-member_count', '-created_at')

    # Pagination
    paginator = Paginator(groups, 12)
    page_number = request.GET.get('page')
    groups_page = paginator.get_page(page_number)

    # Get user's groups for quick access
    user_groups = []
    if request.user.is_authenticated:
        try:
            patient_profile = request.user.patientprofile
            user_groups = SupportGroup.objects.filter(
                memberships__patient=patient_profile,
                memberships__is_active=True
            )
        except PatientProfile.DoesNotExist:
            pass

    context = {
        'groups': groups_page,
        'user_groups': user_groups,
        'category': category,
        'search': search,
        'categories': SupportGroup.GROUP_TYPES,
    }

    return render(request, 'support_groups/list.html', context)

@login_required
def create_group(request):
    """Create new support group"""
    if request.method == 'POST':
        messages.info(request, 'Group creation functionality will be implemented.')
        return redirect('support_groups:list')
    return render(request, 'support_groups/create.html')

@login_required
def group_detail(request, group_id):
    """Support group detail"""
    group = get_object_or_404(SupportGroup, id=group_id, is_active=True)

    # Check membership
    is_member = False
    membership = None
    try:
        patient_profile = request.user.patientprofile
        membership = GroupMembership.objects.filter(
            group=group,
            patient=patient_profile,
            is_active=True
        ).first()
        is_member = membership is not None
    except PatientProfile.DoesNotExist:
        pass

    # Get recent posts
    recent_posts = GroupDiscussion.objects.filter(group=group).order_by('-created_at')[:10]

    # Get upcoming events
    upcoming_events = LiveQASession.objects.filter(
        group=group,
        scheduled_datetime__gte=timezone.now()
    ).order_by('scheduled_datetime')[:3]

    # Get member count
    member_count = GroupMembership.objects.filter(group=group, is_active=True).count()

    context = {
        'group': group,
        'is_member': is_member,
        'membership': membership,
        'recent_posts': recent_posts,
        'upcoming_events': upcoming_events,
        'member_count': member_count,
    }

    return render(request, 'support_groups/detail.html', context)

@login_required
def join_group(request, group_id):
    """Join support group"""
    group = get_object_or_404(SupportGroup, id=group_id, is_active=True)
    membership, created = GroupMembership.objects.get_or_create(
        group=group, user=request.user,
        defaults={'status': 'pending' if group.requires_approval else 'active'}
    )
    if created:
        messages.success(request, f'Successfully joined {group.name}!')
    else:
        messages.info(request, 'You are already a member of this group.')
    return redirect('support_groups:detail', group_id=group_id)

@login_required
def group_discussions(request, group_id):
    """Group discussions"""
    group = get_object_or_404(SupportGroup, id=group_id, is_active=True)

    # Check if user is a member
    try:
        patient_profile = request.user.patientprofile
        membership = GroupMembership.objects.filter(
            group=group,
            patient=patient_profile,
            is_active=True
        ).first()

        if not membership:
            messages.error(request, 'You must be a member to view discussions.')
            return redirect('support_groups:detail', group_id=group_id)
    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    # Handle new post creation
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title and content:
            GroupDiscussion.objects.create(
                group=group,
                author=patient_profile,
                title=title,
                content=content
            )
            messages.success(request, 'Post created successfully!')
            return redirect('support_groups:discussions', group_id=group_id)

    # Get posts with pagination
    posts = GroupDiscussion.objects.filter(group=group).order_by('-created_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    context = {
        'group': group,
        'posts': posts_page,
    }

    return render(request, 'support_groups/discussions.html', context)

@login_required
def post_detail(request, group_id, post_id):
    """Individual post detail with comments"""
    group = get_object_or_404(SupportGroup, id=group_id, is_active=True)
    post = get_object_or_404(GroupDiscussion, id=post_id, group=group)

    # Check if user is a member
    try:
        patient_profile = request.user.patientprofile
        membership = GroupMembership.objects.filter(
            group=group,
            patient=patient_profile,
            is_active=True
        ).first()

        if not membership:
            messages.error(request, 'You must be a member to view this post.')
            return redirect('support_groups:detail', group_id=group_id)
    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    # Handle new comment
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            GroupReply.objects.create(
                discussion=post,
                author=patient_profile,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('support_groups:post_detail', group_id=group_id, post_id=post_id)

    # Get comments
    comments = post.replies.order_by('created_at')

    context = {
        'group': group,
        'post': post,
        'comments': comments,
    }

    return render(request, 'support_groups/post_detail.html', context)

@login_required
def group_events(request, group_id):
    """Group events"""
    group = get_object_or_404(SupportGroup, id=group_id, is_active=True)

    # Check if user is a member
    try:
        patient_profile = request.user.patientprofile
        membership = GroupMembership.objects.filter(
            group=group,
            patient=patient_profile,
            is_active=True
        ).first()

        if not membership:
            messages.error(request, 'You must be a member to view events.')
            return redirect('support_groups:detail', group_id=group_id)
    except PatientProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    # Get upcoming and past events
    now = timezone.now()
    upcoming_events = LiveQASession.objects.filter(
        group=group,
        scheduled_datetime__gte=now
    ).order_by('scheduled_datetime')

    past_events = LiveQASession.objects.filter(
        group=group,
        scheduled_datetime__lt=now
    ).order_by('-scheduled_datetime')[:10]

    context = {
        'group': group,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }

    return render(request, 'support_groups/events.html', context)

@login_required
def my_groups(request):
    """User's support groups dashboard"""
    try:
        patient_profile = request.user.patientprofile

        # Get user's active memberships
        memberships = GroupMembership.objects.filter(
            patient=patient_profile,
            is_active=True
        ).select_related('group')

        # Get recent activity from user's groups
        user_groups = [m.group for m in memberships]
        recent_posts = GroupDiscussion.objects.filter(
            group__in=user_groups
        ).order_by('-created_at')[:10]

        # Get upcoming events
        upcoming_events = LiveQASession.objects.filter(
            group__in=user_groups,
            scheduled_datetime__gte=timezone.now()
        ).order_by('scheduled_datetime')[:5]

        context = {
            'memberships': memberships,
            'recent_posts': recent_posts,
            'upcoming_events': upcoming_events,
        }

    except PatientProfile.DoesNotExist:
        messages.info(request, 'Please complete your profile first.')
        return redirect('patients:profile')

    return render(request, 'support_groups/my_groups.html', context)

@login_required
def leave_group(request, group_id):
    """Leave a support group"""
    if request.method == 'POST':
        try:
            patient_profile = request.user.patientprofile
            group = get_object_or_404(SupportGroup, id=group_id, is_active=True)

            membership = GroupMembership.objects.filter(
                group=group,
                patient=patient_profile,
                is_active=True
            ).first()

            if membership:
                membership.is_active = False
                membership.left_at = timezone.now()
                membership.save()
                messages.success(request, f'You have left {group.name}')
            else:
                messages.error(request, 'You are not a member of this group')

        except PatientProfile.DoesNotExist:
            messages.error(request, 'Profile not found')

    return redirect('support_groups:my_groups')

@login_required
def qa_sessions(request):
    """Live Q&A sessions"""
    # Get upcoming Q&A events across all groups
    upcoming_qa = LiveQASession.objects.filter(
        scheduled_datetime__gte=timezone.now()
    ).order_by('scheduled_datetime')

    # Get past Q&A sessions
    past_qa = LiveQASession.objects.filter(
        scheduled_datetime__lt=timezone.now()
    ).order_by('-scheduled_datetime')[:10]

    context = {
        'upcoming_qa': upcoming_qa,
        'past_qa': past_qa,
    }

    return render(request, 'support_groups/qa_sessions.html', context)

@login_required
def create_group(request):
    """Create a new support group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        group_type = request.POST.get('group_type')
        is_public = request.POST.get('is_public') == 'on'
        requires_approval = request.POST.get('requires_approval') == 'on'
        location = request.POST.get('location', '')
        guidelines = request.POST.get('guidelines', '')

        if name and description and group_type:
            group = SupportGroup.objects.create(
                name=name,
                description=description,
                group_type=group_type,
                is_public=is_public,
                requires_approval=requires_approval,
                location=location,
                guidelines=guidelines,
                created_by=request.user
            )

            # Make creator a member and moderator
            GroupMembership.objects.create(
                group=group,
                user=request.user,
                status='active'
            )
            group.moderators.add(request.user)

            messages.success(request, f'Support group "{group.name}" created successfully!')
            return redirect('support_groups:detail', group_id=group.id)
        else:
            messages.error(request, 'Please fill in all required fields.')

    context = {
        'group_types': SupportGroup.GROUP_TYPES,
    }
    return render(request, 'support_groups/create.html', context)
