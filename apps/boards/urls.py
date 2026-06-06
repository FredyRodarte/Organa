from django.urls import path
from apps.boards.views import list_boards, create_board_view, board_detail_view, update_board_view, delete_board_view
from apps.columns.views import list_columns_view

urlpatterns = [
    path('', list_boards, name='list_boards'),
    path('create', create_board_view, name='create_board'),
    path('<int:board_id>/', board_detail_view, name='board_detail'),
    path('<int:board_id>/update', update_board_view, name='update_board'),
    path('<int:board_id>/delete', delete_board_view, name='delete_board'),
    path('<int:board_id>/columns', list_columns_view, name='list_board_columns'),
]
