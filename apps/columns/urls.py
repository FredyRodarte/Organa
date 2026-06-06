from django.urls import path
from apps.columns.views import create_column_view, reorder_columns_view

urlpatterns = [
    path('create', create_column_view, name='create_column'),
    path('reorder', reorder_columns_view, name='reorder_columns'),
]
