import json
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.urls import resolve, Resolver404
from django.shortcuts import get_object_or_404
from apps.authentication.services import rbac_service
from apps.boards.models import KanbanBoard
from apps.columns.models import KanbanColumn
from apps.cards.models import KanbanCard
from apps.user_stories.models import UserStory
from apps.tasks.models import TechnicalTask

PERMISSION_MAP = {
    # Historias de Usuario (Product Owner)
    'create_story': 'create_stories',
    'update_story': 'create_stories',
    'link_card': 'create_stories',
    'approve_story': 'approve_stories',
    'reject_story': 'reject_stories',
    'request_changes': 'approve_stories',
    
    # Columnas (Scrum Master)
    'create_column': 'manage_columns',
    'update_column': 'manage_columns',
    'delete_column': 'manage_columns',
    'reorder_columns': 'manage_columns',
    
    # Tablero (Scrum Master)
    'update_board': 'manage_board',
    'delete_board': 'manage_board',
    
    # Tarjetas y Subtareas (Developer)
    'create_card': 'create_tasks',
    'update_card': 'update_tasks',
    'delete_card': 'update_tasks',
    'move_card': 'move_cards',
    'create_task': 'create_tasks',
    'update_task': 'update_tasks',
    'delete_task': 'update_tasks',
}

class RolePermissionMiddleware:
    """
    Middleware encargado de interceptar las solicitudes y verificar
    los permisos del rol Scrum del usuario y la propiedad del recurso.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Si el usuario no está autenticado, dejar pasar a los decorators estándar (login_required, etc.)
        if not request.user or not request.user.is_authenticated:
            return self.get_response(request)

        try:
            match = resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        view_name = match.url_name
        
        # 2. Si la vista actual está en el mapa de permisos, validar
        if view_name in PERMISSION_MAP:
            required_permission = PERMISSION_MAP[view_name]
            
            # A. Validar rol y permiso Scrum
            if not rbac_service.validate_permission(request.user, required_permission):
                return JsonResponse({
                    "status": "error", 
                    "message": f"No tienes los permisos Scrum requeridos para esta acción ({required_permission})."
                }, status=403)

            # B. Validar ownership (propiedad del tablero del recurso)
            try:
                board_id = match.kwargs.get('board_id')
                story_id = match.kwargs.get('story_id')
                column_id = match.kwargs.get('column_id')
                card_id = match.kwargs.get('card_id')
                task_id = match.kwargs.get('task_id')

                # Si es un POST/PUT JSON, intentar leer del cuerpo
                if request.method in ['POST', 'PUT', 'DELETE', 'PATCH'] and request.content_type == 'application/json':
                    try:
                        body_data = json.loads(request.body)
                        if not board_id:
                            board_id = body_data.get('board_id')
                        if not story_id:
                            story_id = body_data.get('story_id')
                        if not column_id:
                            column_id = body_data.get('column_id') or body_data.get('target_column_id') or body_data.get('target_column')
                        if not card_id:
                            card_id = body_data.get('card_id')
                        if not task_id:
                            task_id = body_data.get('task_id')
                    except Exception:
                        pass

                # Validar de forma secuencial según el identificador de recurso encontrado
                if board_id:
                    obj = get_object_or_404(KanbanBoard, id=board_id)
                    rbac_service.validate_ownership(request.user, obj)
                elif story_id:
                    obj = get_object_or_404(UserStory, id=story_id)
                    rbac_service.validate_ownership(request.user, obj)
                elif column_id:
                    obj = get_object_or_404(KanbanColumn, id=column_id)
                    rbac_service.validate_ownership(request.user, obj)
                elif card_id:
                    obj = get_object_or_404(KanbanCard, id=card_id)
                    rbac_service.validate_ownership(request.user, obj)
                elif task_id:
                    obj = get_object_or_404(TechnicalTask, id=task_id)
                    rbac_service.validate_ownership(request.user, obj)
            except PermissionDenied as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=403)

        return self.get_response(request)
