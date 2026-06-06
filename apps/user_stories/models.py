from django.db import models
from django.conf import settings
from apps.boards.models import KanbanBoard

class UserStory(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Activa'),
        ('COMPLETED', 'Completada'),
        ('ARCHIVED', 'Archivada'),
    ]

    board = models.ForeignKey(
        KanbanBoard,
        on_delete=models.CASCADE,
        related_name='user_stories'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_stories'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    business_value = models.PositiveIntegerField(default=0)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['board', 'title'],
                name='unique_board_story_title'
            )
        ]
        indexes = [
            models.Index(fields=['board', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} (Val: {self.business_value}, Pri: {self.priority}) en {self.board.name}"
