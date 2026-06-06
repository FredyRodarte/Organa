import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from apps.boards.services import board_service

@login_required
@require_http_methods(["GET"])
def list_boards(request):
    """
    Retorna todos los tableros del usuario autenticado en formato JSON.
    """
    try:
        boards = board_service.get_user_boards(request.user)
        data = [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description or "",
                "created_at": b.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for b in boards
        ]
        return JsonResponse({"status": "success", "boards": data}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error del servidor: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def create_board_view(request):
    """
    Recibe un JSON con los datos del tablero, valida y lo crea usando la Service Layer.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
    
    name = data.get("name")
    description = data.get("description")
    
    try:
        board = board_service.create_board(request.user, name, description)
        
        from apps.authentication.services import rbac_service
        rbac_service.log_action(
            user=request.user,
            action='BOARD_CREATE',
            description=f"Tablero '{board.name}' (ID: {board.id}) creado."
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Tablero creado correctamente.",
            "board": {
                "id": board.id,
                "name": board.name,
                "description": board.description or "",
                "created_at": board.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=201)
    except ValidationError as e:
        # Extraer el mensaje del error de validación
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al procesar la solicitud: {str(e)}"}, status=500)

from django.shortcuts import render

@login_required
@require_http_methods(["GET"])
def board_detail_view(request, board_id):
    """
    Renderiza la página de detalle individual para un tablero Kanban,
    validando la propiedad de forma estricta.
    """
    board = board_service.get_board_for_user(request.user, board_id)
    return render(request, 'boards/board_detail.html', {'board': board})

from django.core.exceptions import PermissionDenied

@login_required
@require_http_methods(["POST"])
def update_board_view(request, board_id):
    """
    Recibe un JSON con los campos a modificar, valida y actualiza el tablero usando la Service Layer.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    name = data.get("name")
    description = data.get("description")
    
    try:
        board = board_service.update_board(request.user, board_id, name, description)
        
        from apps.authentication.services import rbac_service
        rbac_service.log_action(
            user=request.user,
            action='BOARD_UPDATE',
            description=f"Tablero '{board.name}' (ID: {board.id}) modificado."
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Tablero modificado correctamente.",
            "board": {
                "id": board.id,
                "name": board.name,
                "description": board.description or "",
                "created_at": board.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al modificar el tablero: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def delete_board_view(request, board_id):
    """
    Elimina el tablero especificado tras validar propiedad en la Service Layer.
    """
    try:
        from apps.boards.models import KanbanBoard
        from django.shortcuts import get_object_or_404
        from apps.authentication.services import rbac_service
        board = get_object_or_404(KanbanBoard, id=board_id)
        
        board_service.delete_board(request.user, board_id)
        
        rbac_service.log_action(
            user=request.user,
            action='BOARD_DELETE',
            description=f"Tablero '{board.name}' (ID: {board.id}) eliminado."
        )
        return JsonResponse({
            "status": "success",
            "message": "Tablero eliminado correctamente."
        }, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al eliminar el tablero: {str(e)}"}, status=500)
