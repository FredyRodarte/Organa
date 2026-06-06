from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from apps.user_stories.models import UserStory
from apps.boards.services import board_service
from apps.cards.models import KanbanCard

def validate_story(title, priority, status, business_value):
    """
    Valida los atributos de una historia de usuario.
    """
    if not title or not title.strip():
        raise ValidationError("El título de la historia de usuario es obligatorio.")
    
    valid_priorities = [choice[0] for choice in UserStory.PRIORITY_CHOICES]
    if priority not in valid_priorities:
        raise ValidationError(f"La prioridad '{priority}' no es válida.")
        
    valid_statuses = [choice[0] for choice in UserStory.STATUS_CHOICES]
    if status not in valid_statuses:
        raise ValidationError(f"El estado '{status}' no es válido.")

    if business_value is not None:
        try:
            val = int(business_value)
            if val < 0:
                raise ValidationError("El valor de negocio debe ser un número entero positivo o cero.")
        except (ValueError, TypeError):
            raise ValidationError("El valor de negocio debe ser un número entero válido.")

def create_story(user, board_id, title, description=None, business_value=0, priority='MEDIUM', status='ACTIVE'):
    """
    Crea una historia de usuario tras validar la propiedad del tablero.
    """
    # Validar propiedad del tablero
    board = board_service.get_board_for_user(user, board_id)
    
    title_clean = title.strip() if title else ""
    description_clean = description.strip() if description else None
    
    validate_story(title_clean, priority, status, business_value)

    # Validar unicidad del título dentro del tablero
    if UserStory.objects.filter(board=board, title__iexact=title_clean).exists():
        raise ValidationError(f"Ya existe una historia de usuario llamada '{title_clean}' en este tablero.")

    try:
        story = UserStory.objects.create(
            board=board,
            created_by=user,
            title=title_clean,
            description=description_clean,
            business_value=business_value,
            priority=priority,
            status=status
        )
        return story
    except IntegrityError:
        raise ValidationError("Error de integridad al guardar la historia de usuario.")

def update_story(user, story_id, title, description=None, business_value=0, priority='MEDIUM', status='ACTIVE'):
    """
    Actualiza una historia de usuario tras validar propiedad.
    """
    story = get_object_or_404(UserStory, id=story_id)
    
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, story.board_id)
    
    title_clean = title.strip() if title else ""
    description_clean = description.strip() if description else None
    
    validate_story(title_clean, priority, status, business_value)

    # Validar duplicados exceptuando la propia historia
    if UserStory.objects.filter(board_id=story.board_id, title__iexact=title_clean).exclude(id=story.id).exists():
        raise ValidationError(f"Ya existe una historia de usuario llamada '{title_clean}' en este tablero.")

    story.title = title_clean
    story.description = description_clean
    story.business_value = int(business_value)
    story.priority = priority
    story.status = status
    story.save()
    return story

def get_board_stories(user, board_id):
    """
    Retorna todas las historias de usuario asociadas a un tablero tras validar propiedad.
    """
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, board_id)
    return UserStory.objects.filter(board_id=board_id)

def link_card_to_story(user, card_id, story_id=None):
    """
    Asocia (o desasocia) una tarjeta Kanban a una historia de usuario.
    Valida pertenencia de ambos al mismo tablero y ownership.
    """
    card = get_object_or_404(KanbanCard, id=card_id)
    
    # Validar propiedad del tablero de la tarjeta
    board_service.get_board_for_user(user, card.column.board_id)

    if story_id:
        story = get_object_or_404(UserStory, id=story_id)
        
        # Validar propiedad del tablero de la historia
        board_service.get_board_for_user(user, story.board_id)

        # Validar integridad referencial (mismo tablero)
        if card.column.board_id != story.board_id:
            raise ValidationError("No puedes asociar una tarjeta a una historia de usuario de otro tablero.")
            
        card.user_story = story
    else:
        card.user_story = None
        
    card.save()
    return card
