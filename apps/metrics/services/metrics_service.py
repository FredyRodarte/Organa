from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404
from apps.boards.models import KanbanBoard
from apps.columns.models import KanbanColumn
from apps.cards.models import KanbanCard
from apps.user_stories.models import UserStory
from apps.authentication.services import rbac_service

def get_completion_rate(completed, total):
    """
    Calcula el porcentaje de completitud.
    """
    if not total:
        return 0.0
    return round((completed / total) * 100.0, 1)

def get_board_metrics(user, board_id):
    """
    Retorna métricas generales del tablero:
    - total_cards
    - cards_by_column: lista de dicts con {column_id, name, position, count}
    - completed_cards
    - pending_cards
    - completion_rate
    En caso de Developer, se filtran a nivel personal (sólo tarjetas asignadas a él).
    """
    board = get_object_or_404(KanbanBoard, id=board_id)
    rbac_service.validate_ownership(user, board)
    
    role = rbac_service.get_user_role(user)
    
    # 1. Obtener todas las columnas ordenadas por posición
    columns = list(KanbanColumn.objects.filter(board_id=board_id).order_by('position'))
    
    # 2. Identificar columnas de completitud
    completed_names = ["hecho", "done", "completado", "terminado", "finalizado", "listo", "completada"]
    completed_col_ids = [c.id for c in columns if any(name in c.name.lower() for name in completed_names)]
    
    if columns and not completed_col_ids:
        # Fallback a la última columna
        completed_col_ids = [columns[-1].id]
        
    # 3. Consultar y agregar tarjetas
    cards = KanbanCard.objects.filter(column__board_id=board_id)
    
    if role == 'DEVELOPER':
        # Developer sólo ve sus métricas personales
        cards = cards.filter(assigned_to=user)
        
    total_cards = cards.count()
    
    # Agrupar por columna usando query optimizada
    column_counts = cards.values('column_id').annotate(count=Count('id'))
    counts_map = {item['column_id']: item['count'] for item in column_counts}
    
    cards_by_column = []
    completed_cards = 0
    pending_cards = 0
    
    for c in columns:
        cnt = counts_map.get(c.id, 0)
        cards_by_column.append({
            "column_id": c.id,
            "name": c.name,
            "position": c.position,
            "count": cnt
        })
        if c.id in completed_col_ids:
            completed_cards += cnt
        else:
            pending_cards += cnt
            
    completion_rate = get_completion_rate(completed_cards, total_cards)
    
    return {
        "total_cards": total_cards,
        "cards_by_column": cards_by_column,
        "completed_cards": completed_cards,
        "pending_cards": pending_cards,
        "completion_rate": completion_rate
    }

def get_story_metrics(user, board_id):
    """
    Retorna métricas de historias de usuario agrupadas por su estado de aprobación.
    En caso de Developer, sólo se toman en cuenta historias que tienen tarjetas asignadas a él.
    """
    board = get_object_or_404(KanbanBoard, id=board_id)
    rbac_service.validate_ownership(user, board)
    
    role = rbac_service.get_user_role(user)
    
    stories = UserStory.objects.filter(board_id=board_id)
    if role == 'DEVELOPER':
        stories = stories.filter(cards__assigned_to=user).distinct()
        
    total_stories = stories.count()
    
    # Agrupar por approval_status
    status_counts = stories.values('approval_status').annotate(count=Count('id'))
    counts_map = {item['approval_status']: item['count'] for item in status_counts}
    
    return {
        "total_stories": total_stories,
        "approved_stories": counts_map.get('APPROVED', 0),
        "pending_stories": counts_map.get('PENDING', 0),
        "rejected_stories": counts_map.get('REJECTED', 0),
        "changes_requested_stories": counts_map.get('CHANGES_REQUESTED', 0)
    }

def get_assignment_metrics(user, board_id):
    """
    Retorna la carga de trabajo por desarrollador.
    Lanza PermissionDenied si el usuario es un Developer (lock de métricas personales).
    """
    board = get_object_or_404(KanbanBoard, id=board_id)
    rbac_service.validate_ownership(user, board)
    
    role = rbac_service.get_user_role(user)
    if role == 'DEVELOPER':
        raise PermissionDenied("No tienes permisos Scrum para consultar la carga de trabajo del equipo.")
        
    # Obtener conteo agrupado por asignado
    workload = KanbanCard.objects.filter(
        column__board_id=board_id,
        assigned_to__isnull=False
    ).values(
        'assigned_to_id',
        'assigned_to__email',
        'assigned_to__username'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    data = [
        {
            "user_id": item['assigned_to_id'],
            "email": item['assigned_to__email'],
            "username": item['assigned_to__username'],
            "count": item['count']
        }
        for item in workload
    ]
    return data
