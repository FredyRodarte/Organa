from django.db import models
from apps.columns.models import KanbanColumn

class KanbanCard(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
    ]

    column = models.ForeignKey(
        KanbanColumn,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    user_story = models.ForeignKey(
        'user_stories.UserStory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cards'
    )
    status = models.CharField(
        max_length=50,
        default='ACTIVE',
        blank=True,
        null=True
    )
    position = models.PositiveIntegerField(default=0)
    assigned_to = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cards'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_by_cards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'created_at']
        indexes = [
            models.Index(fields=['column', 'position']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['user_story']),
        ]

    def __str__(self):
        return f"{self.title} ({self.priority}) en columna {self.column.name} (pos: {self.position})"

