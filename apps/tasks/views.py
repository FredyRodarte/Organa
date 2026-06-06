import json
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, PermissionDenied
from apps.tasks.services import task_service

@login_required
@require_http_methods(["POST"])
def create_task_view(request):
    """
    Crea una nueva tarea técnica vinculada a una historia de usuario.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)

    story_id = data.get("story_id")
    title = data.get("title")
    description = data.get("description")
    estimated_hours = data.get("estimated_hours", 0)
    status = data.get("status", "TODO")

    if not story_id:
        return JsonResponse({"status": "error", "message": "El ID de la historia (story_id) es obligatorio."}, status=400)

    try:
        task = task_service.create_task(
            request.user, story_id, title, description, estimated_hours, status
        )
        return JsonResponse({
            "status": "success",
            "message": "Tarea técnica creada correctamente.",
            "task": {
                "id": task.id,
                "story_id": task.user_story_id,
                "title": task.title,
                "description": task.description or "",
                "estimated_hours": task.estimated_hours,
                "status": task.status,
                "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=201)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al crear la tarea técnica: {str(e)}"}, status=500)

@login_required
@require_http_methods(["PUT", "POST"])
def update_task_view(request):
    """
    Modifica una tarea técnica tras validar propiedad.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)

    task_id = data.get("task_id")
    title = data.get("title")
    description = data.get("description")
    estimated_hours = data.get("estimated_hours", 0)
    status = data.get("status", "TODO")

    if not task_id:
        return JsonResponse({"status": "error", "message": "El ID de la tarea (task_id) es obligatorio."}, status=400)

    try:
        task = task_service.update_task(
            request.user, task_id, title, description, estimated_hours, status
        )
        return JsonResponse({
            "status": "success",
            "message": "Tarea técnica modificada correctamente.",
            "task": {
                "id": task.id,
                "story_id": task.user_story_id,
                "title": task.title,
                "description": task.description or "",
                "estimated_hours": task.estimated_hours,
                "status": task.status
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La tarea técnica especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al modificar la tarea técnica: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def list_tasks_view(request, story_id):
    """
    Retorna el listado de tareas técnicas de una historia de usuario.
    """
    try:
        tasks = task_service.get_story_tasks(request.user, story_id)
        data = [
            {
                "id": task.id,
                "story_id": task.user_story_id,
                "title": task.title,
                "description": task.description or "",
                "estimated_hours": task.estimated_hours,
                "status": task.status,
                "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for task in tasks
        ]
        return JsonResponse({"status": "success", "tasks": data}, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al obtener tareas técnicas: {str(e)}"}, status=500)

@login_required
@require_http_methods(["DELETE", "POST"])
def delete_task_view(request):
    """
    Elimina una tarea técnica tras validar propiedad.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)

    task_id = data.get("task_id")
    if not task_id:
        return JsonResponse({"status": "error", "message": "El ID de la tarea (task_id) es obligatorio."}, status=400)

    try:
        task_service.delete_task(request.user, task_id)
        return JsonResponse({
            "status": "success",
            "message": "Tarea técnica eliminada correctamente."
        }, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La tarea técnica especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al eliminar la tarea técnica: {str(e)}"}, status=500)
