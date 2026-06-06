from django.urls import path
from apps.user_stories.views import (
    create_story_view,
    update_story_view,
    list_stories_view,
    detail_story_view,
    link_card_view,
    approve_story_view,
    reject_story_view,
    request_changes_view,
    toggle_role_view
)

urlpatterns = [
    path('create', create_story_view, name='create_story'),
    path('update', update_story_view, name='update_story'),
    path('boards/<int:board_id>', list_stories_view, name='list_stories'),
    path('<int:story_id>', detail_story_view, name='detail_story'),
    path('link', link_card_view, name='link_card'),
    path('<int:story_id>/approve', approve_story_view, name='approve_story'),
    path('<int:story_id>/reject', reject_story_view, name='reject_story'),
    path('<int:story_id>/request-changes', request_changes_view, name='request_changes'),
    path('toggle-role', toggle_role_view, name='toggle_role'),
]
