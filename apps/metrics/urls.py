from django.urls import path
from apps.metrics.views import board_metrics_view, story_metrics_view, team_metrics_view

urlpatterns = [
    path('board/<int:board_id>', board_metrics_view, name='board_metrics'),
    path('stories/<int:board_id>', story_metrics_view, name='story_metrics'),
    path('team/<int:board_id>', team_metrics_view, name='team_metrics'),
]
