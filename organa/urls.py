from django.contrib import admin
from django.urls import path, include
from apps.authentication.views import DashboardView, HomeRedirectView, list_users_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('boards/', include('apps.boards.urls')),
    path('columns/', include('apps.columns.urls')),
    path('cards/', include('apps.cards.urls')),
    path('stories/', include('apps.user_stories.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('users/', list_users_view, name='list_users'),
    path('', HomeRedirectView.as_view(), name='home'),
]
