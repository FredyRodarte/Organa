from django.urls import path
from apps.tasks.views import (
    create_task_view,
    update_task_view,
    list_tasks_view,
    delete_task_view
)

urlpatterns = [
    path('create', create_task_view, name='create_task'),
    path('update', update_task_view, name='update_task'),
    path('stories/<int:story_id>', list_tasks_view, name='list_tasks'),
    path('delete', delete_task_view, name='delete_task'),
]
