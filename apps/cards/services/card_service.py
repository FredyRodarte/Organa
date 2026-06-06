from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.cards.models import KanbanCard
from apps.columns.models import KanbanColumn
from apps.boards.services import board_service
from apps.columns.services import column_service

def validate_card(title, priority):
    """
    Valida los atributos de la tarjeta.
    """
    if not title or not title.strip():
        raise ValidationError("El título de la tarjeta es obligatorio.")
        
    valid_priorities = [choice[0] for choice in KanbanCard.PRIORITY_CHOICES]
    if priority not in valid_priorities:
        raise ValidationError(f"La prioridad '{priority}' no es válida.")

def create_card(user, column_id, title, description=None, priority='MEDIUM'):
    """
    Crea una nueva tarjeta en la columna provista tras validar propiedad del tablero.
    """
    # Validar propiedad de la columna (su tablero)
    column = column_service.get_column_for_user(user, column_id)
    
    title_clean = title.strip() if title else ""
    description_clean = description.strip() if description else None
    
    validate_card(title_clean, priority)
    
    from django.db.models import Max
    max_pos = column.cards.aggregate(max_pos=Max('position'))['max_pos']
    position = 0 if max_pos is None else max_pos + 1
    
    card = KanbanCard.objects.create(
        column=column,
        title=title_clean,
        description=description_clean,
        priority=priority,
        position=position
    )
    return card

def update_card(user, card_id, title, description=None, priority='MEDIUM'):
    """
    Modifica el título, descripción y prioridad de una tarjeta tras validar ownership.
    """
    card = get_object_or_404(KanbanCard, id=card_id)
    
    # Validar propiedad del tablero al que pertenece
    board_service.get_board_for_user(user, card.column.board_id)
    
    title_clean = title.strip() if title else ""
    description_clean = description.strip() if description else None
    
    validate_card(title_clean, priority)
    
    card.title = title_clean
    card.description = description_clean
    card.priority = priority
    card.save()
    return card

def move_card(user, card_id, target_column_id):
    """
    Mueve una tarjeta de su columna actual a una columna destino.
    Verifica que ambas columnas pertenezcan al mismo tablero y que el usuario sea el dueño.
    """
    card = get_object_or_404(KanbanCard, id=card_id)
    
    # Validar propiedad del tablero de la tarjeta de origen
    board_service.get_board_for_user(user, card.column.board_id)
    
    # Validar propiedad de la columna de destino
    target_column = column_service.get_column_for_user(user, target_column_id)
    
    # Prevenir mover tarjetas a columnas de tableros distintos
    if card.column.board_id != target_column.board_id:
        raise ValidationError("No puedes mover una tarjeta a un tablero diferente.")
        
    card.column = target_column
    card.save()
    return card

def get_column_cards(user, column_id):
    """
    Retorna todas las tarjetas de una columna ordenada por position tras validar ownership.
    """
    column = column_service.get_column_for_user(user, column_id)
    return column.cards.all().order_by('position', 'created_at')

def delete_card(user, card_id):
    """
    Elimina una tarjeta tras validar ownership del tablero y reordena el resto.
    """
    card = get_object_or_404(KanbanCard, id=card_id)
    board_service.get_board_for_user(user, card.column.board_id)
    
    column = card.column
    card.delete()
    
    from apps.cards.services.card_movement_service import reorder_column_cards
    reorder_column_cards(column)

