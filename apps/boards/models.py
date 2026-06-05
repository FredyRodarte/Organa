from django.db import models
from django.conf import settings

class KanbanBoard(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boards'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_owner_board_name'
            )
        ]
        indexes = [
            models.Index(fields=['owner', 'created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.owner.email or self.owner.username})"
