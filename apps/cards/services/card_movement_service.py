from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.cards.models import KanbanCard
from apps.columns.models import KanbanColumn
from apps.boards.services import board_service
from apps.columns.services import column_service

def reorder_column_cards(column):
    """
    Recalcula las posiciones consecutivas (0, 1, 2...) de todas las tarjetas
    de una columna para asegurar consistencia e impedir huecos.
    """
    cards = list(column.cards.all().order_by('position', 'created_at'))
    for idx, card in enumerate(cards):
        if card.position != idx:
            card.position = idx
            card.save(update_fields=['position', 'updated_at'])

def move_card(user, card_id, source_column_id, target_column_id, position):
    """
    Mueve una tarjeta de columna y/o reordena su posición dentro de la columna.
    Valida ownership del usuario sobre el tablero y previene inconsistencias.
    """
    # 1. Obtener la tarjeta
    card = get_object_or_404(KanbanCard, id=card_id)
    
    # 2. Validar que la columna actual coincida con la indicada como origen
    if card.column_id != int(source_column_id):
        raise ValidationError("La columna de origen no coincide con la columna actual de la tarjeta.")
        
    # 3. Validar ownership del tablero de origen
    board_service.get_board_for_user(user, card.column.board_id)
    
    # 4. Obtener columna destino
    target_column = get_object_or_404(KanbanColumn, id=target_column_id)
    
    # 5. Validar ownership del tablero de destino
    board_service.get_board_for_user(user, target_column.board_id)
    
    # 6. Prevenir movimientos entre tableros diferentes
    if card.column.board_id != target_column.board_id:
        raise ValidationError("No puedes mover tarjetas entre diferentes tableros.")
        
    try:
        position = int(position)
        if position < 0:
            position = 0
    except (ValueError, TypeError):
        raise ValidationError("La posición destino debe ser un número entero válido.")

    with transaction.atomic():
        if int(source_column_id) == int(target_column_id):
            # Caso A: Reordenamiento dentro de la misma columna
            cards = list(card.column.cards.exclude(id=card.id).order_by('position', 'created_at'))
            
            # Ajustar posición si excede el rango
            if position > len(cards):
                position = len(cards)
                
            # Insertar en la posición deseada
            cards.insert(position, card)
            
            # Guardar nuevas posiciones
            for idx, c in enumerate(cards):
                c.position = idx
                c.save(update_fields=['position', 'updated_at'])
        else:
            # Caso B: Movimiento entre diferentes columnas
            source_column = card.column
            
            # Obtener tarjetas de la columna destino (excluyendo a la misma si ya existiera por alguna razón)
            target_cards = list(target_column.cards.exclude(id=card.id).order_by('position', 'created_at'))
            
            # Ajustar posición si excede el rango
            if position > len(target_cards):
                position = len(target_cards)
                
            # Cambiar de columna la tarjeta
            card.column = target_column
            card.position = position
            card.save(update_fields=['column', 'position', 'updated_at'])
            
            # Insertar en la lista y actualizar posiciones consecutivas de la columna destino
            target_cards.insert(position, card)
            for idx, c in enumerate(target_cards):
                c.position = idx
                c.save(update_fields=['position', 'updated_at'])
                
            # Normalizar posiciones de la columna de origen
            reorder_column_cards(source_column)
            
    return card
