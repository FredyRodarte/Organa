from django.urls import path
from apps.columns.views import create_column_view, reorder_columns_view, update_column_view, delete_column_view

urlpatterns = [
    path('create', create_column_view, name='create_column'),
    path('reorder', reorder_columns_view, name='reorder_columns'),
    path('<int:column_id>/update', update_column_view, name='update_column'),
    path('<int:column_id>/delete', delete_column_view, name='delete_column'),
]
