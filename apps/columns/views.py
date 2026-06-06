import json
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, PermissionDenied
from apps.boards.services import board_service
from apps.columns.services import column_service

@login_required
@require_http_methods(["POST"])
def create_column_view(request):
    """
    Crea una nueva columna en el tablero provisto si el usuario es el dueño.
    Retorna los datos de la columna creada en formato JSON.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
    
    board_id = data.get("board_id")
    name = data.get("name")
    position = data.get("position")
    
    if not board_id:
        return JsonResponse({"status": "error", "message": "El ID del tablero (board_id) es obligatorio."}, status=400)
        
    try:
        # Validar propiedad del tablero
        board = board_service.get_board_for_user(request.user, board_id)
        
        # Validar y convertir posición si se provee
        if position is not None:
            try:
                position = int(position)
                if position <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return JsonResponse({"status": "error", "message": "La posición debe ser un número entero positivo."}, status=400)
                
        column = column_service.create_column(board, name, position)
        return JsonResponse({
            "status": "success",
            "message": "Columna creada correctamente.",
            "column": {
                "id": column.id,
                "name": column.name,
                "position": column.position,
                "created_at": column.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, status=201)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al crear la columna: {str(e)}"}, status=500)

@login_required
@require_http_methods(["GET"])
def list_columns_view(request, board_id):
    """
    Lista todas las columnas ordenadas pertenecientes a un tablero tras validar ownership.
    """
    try:
        # Validar propiedad del tablero
        board = board_service.get_board_for_user(request.user, board_id)
        columns = column_service.get_board_columns(board)
        
        data = [
            {
                "id": col.id,
                "name": col.name,
                "position": col.position,
                "created_at": col.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for col in columns
        ]
        return JsonResponse({"status": "success", "columns": data}, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al obtener columnas: {str(e)}"}, status=500)

@login_required
@require_http_methods(["PUT", "POST"])
def reorder_columns_view(request):
    """
    Reordena las columnas de un tablero en base a una lista ordenada de IDs de columna.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    board_id = data.get("board_id")
    column_ids = data.get("column_ids")
    
    if not board_id:
        return JsonResponse({"status": "error", "message": "El ID del tablero (board_id) es obligatorio."}, status=400)
    if not isinstance(column_ids, list):
        return JsonResponse({"status": "error", "message": "El parámetro 'column_ids' debe ser una lista de IDs."}, status=400)
        
    try:
        # Validar propiedad del tablero
        board = board_service.get_board_for_user(request.user, board_id)
        
        # Validar que todos los IDs sean enteros
        try:
            column_ids = [int(cid) for cid in column_ids]
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "Los IDs de las columnas deben ser números enteros."}, status=400)
            
        updated_columns = column_service.reorder_columns(board, column_ids)
        data = [
            {
                "id": col.id,
                "name": col.name,
                "position": col.position
            }
            for col in updated_columns
        ]
        return JsonResponse({
            "status": "success",
            "message": "Columnas reordenadas correctamente.",
            "columns": data
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "El tablero especificado no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al reordenar columnas: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def update_column_view(request, column_id):
    """
    Actualiza el nombre de una columna Kanban tras validar propiedad y nombre único.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Formato de datos JSON inválido."}, status=400)
        
    name = data.get("name")
    
    try:
        column = column_service.update_column(request.user, column_id, name)
        return JsonResponse({
            "status": "success",
            "message": "Columna modificada correctamente.",
            "column": {
                "id": column.id,
                "name": column.name,
                "position": column.position
            }
        }, status=200)
    except ValidationError as e:
        msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({"status": "error", "message": msg}, status=400)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La columna especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al modificar la columna: {str(e)}"}, status=500)

@login_required
@require_http_methods(["POST"])
def delete_column_view(request, column_id):
    """
    Elimina una columna Kanban tras validar propiedad y normaliza el orden del resto.
    """
    try:
        column_service.delete_column(request.user, column_id)
        return JsonResponse({
            "status": "success",
            "message": "Columna eliminada correctamente."
        }, status=200)
    except PermissionDenied as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=403)
    except Http404:
        return JsonResponse({"status": "error", "message": "La columna especificada no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error al eliminar la columna: {str(e)}"}, status=500)
