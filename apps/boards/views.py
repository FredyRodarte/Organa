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
