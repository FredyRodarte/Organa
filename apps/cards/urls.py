from django.urls import path
from apps.cards.views import (
    create_card_view, update_card_view, move_card_view, list_cards_view, delete_card_view,
    assign_card_view, reassign_card_view, unassign_card_view, get_user_cards_view
)

urlpatterns = [
    path('create', create_card_view, name='create_card'),
    path('update', update_card_view, name='update_card'),
    path('move', move_card_view, name='move_card'),
    path('delete', delete_card_view, name='delete_card'),
    path('columns/<int:column_id>/cards', list_cards_view, name='list_cards'),
    path('<int:card_id>/assign', assign_card_view, name='assign_card'),
    path('<int:card_id>/reassign', reassign_card_view, name='reassign_card'),
    path('<int:card_id>/unassign', unassign_card_view, name='unassign_card'),
    path('users/<int:user_id>/cards', get_user_cards_view, name='get_user_cards'),
]
