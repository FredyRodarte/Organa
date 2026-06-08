from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from apps.metrics.services import metrics_service

@login_required
@require_http_methods(["GET"])
def board_metrics_view(request, board_id):
    """
    Endpoint para obtener métricas generales de tarjetas de un tablero.
    """
    try:
        data = metrics_service.get_board_metrics(request.user, board_id)
        return JsonResponse({"status": "success", "metrics": data}, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe o no tienes acceso."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error del servidor: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def story_metrics_view(request, board_id):
    """
    Endpoint para obtener métricas de aprobación de historias de usuario del tablero.
    """
    try:
        data = metrics_service.get_story_metrics(request.user, board_id)
        return JsonResponse({"status": "success", "metrics": data}, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe o no tienes acceso."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error del servidor: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def team_metrics_view(request, board_id):
    """
    Endpoint para obtener la carga de trabajo del equipo de desarrollo del tablero.
    """
    try:
        data = metrics_service.get_assignment_metrics(request.user, board_id)
        return JsonResponse({"status": "success", "workload": data}, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe o no tienes acceso."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error del servidor: {str(e)}"}, status=500)
