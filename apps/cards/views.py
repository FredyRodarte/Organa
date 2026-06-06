import json
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, PermissionDenied
from apps.cards.services import card_service

@login_required
@require_http_methods(["POST"])
def create_card_view(request):
    """
    Crea una nueva tarjeta en la columna destino tras validar ownership.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    column_id = data.get("column_id")
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "MEDIUM")
    
    if not column_id:
        return JsonResponse({"status": "error", "message": "El ID de la columna (column_id) es obligatorio."}, status=400)
        
    try:
        card = card_service.create_card(request.user, column_id, title, description, priority)
        return JsonResponse({
            "status": "success",
            "message": "Tarjeta creada correctamente.",
            "card": {
                "id": card.id,
                "column_id": card.column_id,
                "title": card.title,
                "description": card.description or "",
                "priority": card.priority,
                "status": card.status,
                "created_at": card.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=201)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La columna especificada no existe o no tienes permisos sobre ella."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al crear la tarjeta: {str(e)}"}, status=500)

@login_required
@require_http_methods(["PUT", "POST"])
def update_card_view(request):
    """
    Modifica los datos de una tarjeta Kanban tras validar ownership.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    card_id = data.get("card_id")
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "MEDIUM")
    
    if not card_id:
        return JsonResponse({"status": "error", "message": "El ID de la tarjeta (card_id) es obligatorio."}, status=400)
        
    try:
        card = card_service.update_card(request.user, card_id, title, description, priority)
        return JsonResponse({
            "status": "success",
            "message": "Tarjeta modificada correctamente.",
            "card": {
                "id": card.id,
                "column_id": card.column_id,
                "title": card.title,
                "description": card.description or "",
                "priority": card.priority,
                "status": card.status
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La tarjeta especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al modificar la tarjeta: {str(e)}"}, status=500)

@login_required
@require_http_methods(["PUT", "POST"])
def move_card_view(request):
    """
    Mueve una tarjeta Kanban a otra columna del mismo tablero tras validar ownership.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    card_id = data.get("card_id")
    target_column_id = data.get("target_column_id")
    
    if not card_id or not target_column_id:
        return JsonResponse({"status": "error", "message": "Los parámetros 'card_id' y 'target_column_id' son obligatorios."}, status=400)
        
    try:
        card = card_service.move_card(request.user, card_id, target_column_id)
        return JsonResponse({
            "status": "success",
            "message": "Tarjeta movida correctamente.",
            "card": {
                "id": card.id,
                "column_id": card.column_id,
                "title": card.title
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La tarjeta o la columna especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al mover la tarjeta: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def list_cards_view(request, column_id):
    """
    Retorna el listado de tarjetas ordenadas pertenecientes a la columna provista.
    """
    try:
        cards = card_service.get_column_cards(request.user, column_id)
        data = [
            {
                "id": card.id,
                "column_id": card.column_id,
                "title": card.title,
                "description": card.description or "",
                "priority": card.priority,
                "status": card.status,
                "created_at": card.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for card in cards
        ]
        return JsonResponse({"status": "success", "cards": data}, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La columna especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al obtener tarjetas: {str(e)}"}, status=500)

@login_required
@require_http_methods(["DELETE", "POST"])
def delete_card_view(request):
    """
    Elimina una tarjeta Kanban tras validar ownership.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    card_id = data.get("card_id")
    if not card_id:
        return JsonResponse({"status": "error", "message": "El ID de la tarjeta (card_id) es obligatorio."}, status=400)
        
    try:
        card_service.delete_card(request.user, card_id)
        return JsonResponse({
            "status": "success",
            "message": "Tarjeta eliminada correctamente."
        }, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La tarjeta especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al eliminar la tarjeta: {str(e)}"}, status=500)

