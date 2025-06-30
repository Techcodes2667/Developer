from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from patients.models import PatientProfile

class SupportGroup(models.Model):
    """Support groups for patients"""
    GROUP_TYPES = [
        ('general', 'General Diabetes Support'),
        ('type1', 'Type 1 Diabetes'),
        ('type2', 'Type 2 Diabetes'),
        ('gestational', 'Gestational Diabetes'),
        ('newly_diagnosed', 'Newly Diagnosed'),
        ('teens', 'Teen Support'),
        ('parents', 'Parents of Diabetic Children'),
        ('mental_health', 'Mental Health Support'),
        ('nutrition', 'Nutrition & Diet'),
        ('exercise', 'Exercise & Fitness'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    group_type = models.CharField(max_length=30, choices=GROUP_TYPES)
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    max_members = models.IntegerField(null=True, blank=True)

    # Moderation
    moderators = models.ManyToManyField(User, related_name='moderated_groups', blank=True)
    guidelines = models.TextField(blank=True)

    # Location-based (optional)
    location = models.CharField(max_length=100, blank=True, help_text="e.g., Kisumu, Kenya")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()

class GroupMembership(models.Model):
    """Membership in support groups"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    ]

    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['group', 'user']

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupDiscussion(models.Model):
    """Discussion topics in support groups"""
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_discussions')
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return f"{self.title} in {self.group.name}"

    @property
    def reply_count(self):
        return self.replies.count()

    @property
    def last_activity(self):
        last_reply = self.replies.order_by('-created_at').first()
        return last_reply.created_at if last_reply else self.created_at

class GroupReply(models.Model):
    """Replies to group discussions"""
    discussion = models.ForeignKey(GroupDiscussion, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author.username} to {self.discussion.title}"

class GroupMessage(models.Model):
    """Private messages between group members"""
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='private_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_group_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

class LiveQASession(models.Model):
    """Live Q&A sessions for support groups"""
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='qa_sessions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_qa_sessions')
    scheduled_datetime = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    meeting_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_datetime']

    def __str__(self):
        return f"Q&A: {self.title} in {self.group.name}"

    @property
    def is_upcoming(self):
        return self.scheduled_datetime > timezone.now()

    @property
    def is_live(self):
        now = timezone.now()
        start_time = self.scheduled_datetime
        end_time = start_time + timezone.timedelta(minutes=self.duration_minutes)
        return start_time <= now <= end_time

class QAQuestion(models.Model):
    """Questions for live Q&A sessions"""
    session = models.ForeignKey(LiveQASession, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    asker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qa_questions')
    answer = models.TextField(blank=True)
    is_answered = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upvotes', '-created_at']

    def __str__(self):
        return f"Question by {self.asker.username} in {self.session.title}"
