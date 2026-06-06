import json
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from apps.user_stories.services import user_story_service, approval_service
from apps.user_stories.models import UserStory

@login_required
@require_http_methods(["POST"])
def create_story_view(request):
    """
    Crea una nueva historia de usuario tras validar propiedad del tablero.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    board_id = data.get("board_id")
    title = data.get("title")
    description = data.get("description")
    business_value = data.get("business_value", 0)
    priority = data.get("priority", "MEDIUM")
    status = data.get("status", "ACTIVE")
    
    if not board_id:
        return JsonResponse({"status": "error", "message": "El ID del tablero (board_id) es obligatorio."}, status=400)
        
    try:
        story = user_story_service.create_story(
            request.user, board_id, title, description, business_value, priority, status
        )
        return JsonResponse({
            "status": "success",
            "message": "Historia de usuario creada correctamente.",
            "story": {
                "id": story.id,
                "title": story.title,
                "description": story.description or "",
                "business_value": story.business_value,
                "priority": story.priority,
                "status": story.status,
                "created_at": story.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tasks": 0,
                "completed_tasks": 0,
                "total_hours": 0,
                "approval_status": story.approval_status,
                "approved_by_email": None,
                "approved_at": None,
                "rejection_reason": None
            }
        }, status=201)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe o no tienes permisos sobre él."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al crear la historia de usuario: {str(e)}"}, status=500)

@login_required
@require_http_methods(["PUT", "POST"])
def update_story_view(request):
    """
    Modifica una historia de usuario tras validar propiedad.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    story_id = data.get("story_id")
    title = data.get("title")
    description = data.get("description")
    business_value = data.get("business_value", 0)
    priority = data.get("priority", "MEDIUM")
    status = data.get("status", "ACTIVE")
    
    if not story_id:
        return JsonResponse({"status": "error", "message": "El ID de la historia (story_id) es obligatorio."}, status=400)
        
    try:
        story = user_story_service.update_story(
            request.user, story_id, title, description, business_value, priority, status
        )
        return JsonResponse({
            "status": "success",
            "message": "Historia de usuario modificada correctamente.",
            "story": {
                "id": story.id,
                "title": story.title,
                "description": story.description or "",
                "business_value": story.business_value,
                "priority": story.priority,
                "status": story.status,
                "total_tasks": story.tasks.count(),
                "completed_tasks": story.tasks.filter(status='DONE').count(),
                "total_hours": sum(t.estimated_hours for t in story.tasks.all()),
                "approval_status": story.approval_status,
                "approved_by_email": story.approved_by.email or story.approved_by.username if story.approved_by else None,
                "approved_at": story.approved_at.strftime("%Y-%m-%d %H:%M:%S") if story.approved_at else None,
                "rejection_reason": story.rejection_reason
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al modificar la historia de usuario: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def list_stories_view(request, board_id):
    """
    Retorna el listado de historias de usuario pertenecientes al tablero.
    """
    try:
        from apps.authentication.services import rbac_service
        has_metrics_permission = rbac_service.validate_permission(request.user, 'view_metrics')
        
        stories = user_story_service.get_board_stories(request.user, board_id)
        data = [
            {
                "id": story.id,
                "title": story.title,
                "description": story.description or "",
                "business_value": story.business_value,
                "priority": story.priority,
                "status": story.status,
                "created_at": story.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tasks": story.tasks.count() if has_metrics_permission else 0,
                "completed_tasks": story.tasks.filter(status='DONE').count() if has_metrics_permission else 0,
                "total_hours": sum(t.estimated_hours for t in story.tasks.all()) if has_metrics_permission else 0,
                "approval_status": story.approval_status,
                "approved_by_email": story.approved_by.email or story.approved_by.username if story.approved_by else None,
                "approved_at": story.approved_at.strftime("%Y-%m-%d %H:%M:%S") if story.approved_at else None,
                "rejection_reason": story.rejection_reason
            }
            for story in stories
        ]
        return JsonResponse({
            "status": "success",
            "user_role": getattr(request.user, 'role', 'DEV'),
            "stories": data
        }, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al obtener historias de usuario: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def detail_story_view(request, story_id):
    """
    Retorna los detalles de una historia de usuario, incluyendo las tarjetas Kanban asociadas.
    """
    try:
        story = get_object_or_404(UserStory, id=story_id)
        from apps.boards.services import board_service
        board_service.get_board_for_user(request.user, story.board_id)
        
        cards = story.cards.all()
        cards_data = [
            {
                "id": card.id,
                "title": card.title,
                "column_id": card.column_id,
                "column_name": card.column.name,
                "priority": card.priority,
                "status": card.status
            }
            for card in cards
        ]
        
        tasks = story.tasks.all()
        tasks_data = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "status": task.status,
                "estimated_hours": task.estimated_hours
            }
            for task in tasks
        ]
        
        from apps.authentication.services import rbac_service
        has_metrics_permission = rbac_service.validate_permission(request.user, 'view_metrics')
        
        return JsonResponse({
            "status": "success",
            "user_role": getattr(request.user, 'role', 'DEV'),
            "story": {
                "id": story.id,
                "board_id": story.board_id,
                "title": story.title,
                "description": story.description or "",
                "business_value": story.business_value,
                "priority": story.priority,
                "status": story.status,
                "created_at": story.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tasks": len(tasks_data) if has_metrics_permission else 0,
                "completed_tasks": sum(1 for t in tasks_data if t['status'] == 'DONE') if has_metrics_permission else 0,
                "total_hours": sum(t['estimated_hours'] for t in tasks_data) if has_metrics_permission else 0,
                "cards": cards_data,
                "tasks": tasks_data,
                "approval_status": story.approval_status,
                "approved_by_email": story.approved_by.email or story.approved_by.username if story.approved_by else None,
                "approved_at": story.approved_at.strftime("%Y-%m-%d %H:%M:%S") if story.approved_at else None,
                "rejection_reason": story.rejection_reason
            }
        }, status=200)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al obtener detalle de la historia: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def link_card_view(request):
    """
    Asocia o desasocia una tarjeta a una historia de usuario.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    card_id = data.get("card_id")
    story_id = data.get("story_id")  # Puede ser None para desasociar
    
    if not card_id:
        return JsonResponse({"status": "error", "message": "El ID de la tarjeta (card_id) es obligatorio."}, status=400)
        
    try:
        card = user_story_service.link_card_to_story(request.user, card_id, story_id)
        return JsonResponse({
            "status": "success",
            "message": "Tarjeta vinculada correctamente." if story_id else "Tarjeta desvinculada correctamente.",
            "card": {
                "id": card.id,
                "user_story_id": card.user_story_id,
                "title": card.title
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La tarjeta o historia especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al asociar tarjeta: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def approve_story_view(request, story_id):
    """
    Aprueba una historia de usuario tras validar permisos de Product Owner.
    """
    try:
        story = approval_service.approve_story(request.user, story_id)
        return JsonResponse({
            "status": "success",
            "message": "Historia de usuario aprobada correctamente.",
            "story": {
                "id": story.id,
                "approval_status": story.approval_status,
                "approved_by_email": story.approved_by.email or story.approved_by.username if story.approved_by else None,
                "approved_at": story.approved_at.strftime("%Y-%m-%d %H:%M:%S") if story.approved_at else None,
                "rejection_reason": story.rejection_reason
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al aprobar historia: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def reject_story_view(request, story_id):
    """
    Rechaza una historia de usuario especificando un motivo.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    reason = data.get("reason")
    try:
        story = approval_service.reject_story(request.user, story_id, reason)
        return JsonResponse({
            "status": "success",
            "message": "Historia de usuario rechazada.",
            "story": {
                "id": story.id,
                "approval_status": story.approval_status,
                "approved_by_email": story.approved_by.email or story.approved_by.username if story.approved_by else None,
                "approved_at": story.approved_at.strftime("%Y-%m-%d %H:%M:%S") if story.approved_at else None,
                "rejection_reason": story.rejection_reason
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al rechazar historia: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def request_changes_view(request, story_id):
    """
    Solicita cambios en una historia de usuario especificando un motivo.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    reason = data.get("reason")
    try:
        story = approval_service.request_changes(request.user, story_id, reason)
        return JsonResponse({
            "status": "success",
            "message": "Ajustes solicitados correctamente.",
            "story": {
                "id": story.id,
                "approval_status": story.approval_status,
                "approved_by_email": story.approved_by.email or story.approved_by.username if story.approved_by else None,
                "approved_at": story.approved_at.strftime("%Y-%m-%d %H:%M:%S") if story.approved_at else None,
                "rejection_reason": story.rejection_reason
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La historia de usuario especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al solicitar cambios: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def toggle_role_view(request):
    """
    Simula el cambio de rol rotativo (DEV -> PO -> SM -> DEV) del usuario actual.
    """
    try:
        from apps.authentication.services import rbac_service
        user = request.user
        current_role = user.role
        
        # Rotación de rol
        if current_role == 'DEV':
            new_role = 'PO'
            new_role_full = 'PRODUCT_OWNER'
        elif current_role == 'PO':
            new_role = 'SM'
            new_role_full = 'SCRUM_MASTER'
        else:
            new_role = 'DEV'
            new_role_full = 'DEVELOPER'
            
        rbac_service.assign_role(user, new_role_full)
        
        return JsonResponse({
            "status": "success",
            "role": new_role,
            "message": f"Rol cambiado a {user.get_role_display()}."
        }, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al cambiar de rol: {str(e)}"}, status=500)
