from django.db import models
from django.db.models.functions import Lower
from apps.boards.models import KanbanBoard

class KanbanColumn(models.Model):
    board = models.ForeignKey(
        KanbanBoard,
        on_delete=models.CASCADE,
        related_name='columns'
    )
    name = models.CharField(max_length=255)
    position = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(
                fields=['board', 'position'],
                name='unique_board_column_position'
            ),
            models.UniqueConstraint(
                'board',
                Lower('name'),
                name='unique_board_column_name_case_insensitive'
            )
        ]
        indexes = [
            models.Index(fields=['board', 'position']),
        ]

    def __str__(self):
        return f"{self.name} (Pos: {self.position}) en tablero {self.board.name}"
