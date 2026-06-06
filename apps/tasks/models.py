from django.db import models
from apps.user_stories.models import UserStory

class TechnicalTask(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'Por hacer'),
        ('IN_PROGRESS', 'En progreso'),
        ('DONE', 'Completado'),
    ]

    user_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='TODO'
    )
    estimated_hours = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user_story', 'title'],
                name='unique_story_task_title'
            )
        ]
        indexes = [
            models.Index(fields=['user_story', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status}, {self.estimated_hours}h) de historia {self.user_story.title}"
