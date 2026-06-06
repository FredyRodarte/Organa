from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.authentication.models import CustomUser

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/accounts/login/'

class HomeRedirectView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return redirect('/accounts/login/')

@login_required
@require_http_methods(["GET"])
def list_users_view(request):
    """
    Retorna el listado de todos los usuarios registrados en Organa.
    """
    try:
        users = CustomUser.objects.all()
        data = [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "avatar_url": u.avatar_url or "",
                "role": u.role # 'DEV', 'PO', 'SM'
            }
            for u in users
        ]
        return JsonResponse({"status": "success", "users": data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al obtener usuarios: {str(e)}"}, status=500)
