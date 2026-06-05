from django.urls import path
from apps.boards.views import list_boards, create_board_view, board_detail_view

urlpatterns = [
    path('', list_boards, name='list_boards'),
    path('create', create_board_view, name='create_board'),
    path('<int:board_id>/', board_detail_view, name='board_detail'),
]
