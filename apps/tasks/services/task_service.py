from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from apps.tasks.models import TechnicalTask
from apps.user_stories.models import UserStory
from apps.boards.services import board_service

def validate_task(title, status, estimated_hours):
    """
    Valida los atributos de una tarea técnica.
    """
    if not title or not title.strip():
        raise ValidationError("El título de la tarea técnica es obligatorio.")

    valid_statuses = [choice[0] for choice in TechnicalTask.STATUS_CHOICES]
    if status not in valid_statuses:
        raise ValidationError(f"El estado '{status}' no es válido.")

    if estimated_hours is not None:
        try:
            val = int(estimated_hours)
            if val < 0:
                raise ValidationError("Las horas estimadas deben ser un número entero positivo o cero.")
        except (ValueError, TypeError):
            raise ValidationError("Las horas estimadas deben ser un número entero válido.")

def create_task(user, story_id, title, description=None, estimated_hours=0, status='TODO'):
    """
    Crea una tarea técnica vinculada a una historia de usuario tras validar propiedad.
    """
    story = get_object_or_404(UserStory, id=story_id)
    
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, story.board_id)
    
    title_clean = title.strip() if title else ""
    description_clean = description.strip() if description else None

    validate_task(title_clean, status, estimated_hours)

    # Validar duplicidad dentro de la misma historia
    if TechnicalTask.objects.filter(user_story=story, title__iexact=title_clean).exists():
        raise ValidationError(f"Ya existe una tarea llamada '{title_clean}' en esta historia de usuario.")

    try:
        task = TechnicalTask.objects.create(
            user_story=story,
            title=title_clean,
            description=description_clean,
            estimated_hours=estimated_hours,
            status=status
        )
        return task
    except IntegrityError:
        raise ValidationError("Error de integridad al guardar la tarea técnica.")

def update_task(user, task_id, title, description=None, estimated_hours=0, status='TODO'):
    """
    Actualiza una tarea técnica tras validar propiedad.
    """
    task = get_object_or_404(TechnicalTask, id=task_id)
    
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, task.user_story.board_id)

    title_clean = title.strip() if title else ""
    description_clean = description.strip() if description else None

    validate_task(title_clean, status, estimated_hours)

    # Validar duplicados exceptuando la propia tarea
    if TechnicalTask.objects.filter(user_story=task.user_story, title__iexact=title_clean).exclude(id=task.id).exists():
        raise ValidationError(f"Ya existe una tarea llamada '{title_clean}' en esta historia de usuario.")

    task.title = title_clean
    task.description = description_clean
    task.estimated_hours = int(estimated_hours)
    task.status = status
    task.save()
    return task

def get_story_tasks(user, story_id):
    """
    Retorna todas las tareas asociadas a una historia tras validar propiedad.
    """
    story = get_object_or_404(UserStory, id=story_id)
    
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, story.board_id)
    return story.tasks.all()

def delete_task(user, task_id):
    """
    Elimina una tarea técnica tras validar propiedad.
    """
    task = get_object_or_404(TechnicalTask, id=task_id)
    
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, task.user_story.board_id)
    task.delete()
    return task_id
