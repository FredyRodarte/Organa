from django.contrib import admin
from django.urls import path, include
from apps.authentication.views import DashboardView, HomeRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', HomeRedirectView.as_view(), name='home'),
]
