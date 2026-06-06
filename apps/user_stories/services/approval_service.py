from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.user_stories.models import UserStory
from apps.boards.services import board_service

def validate_po_permissions(user, story):
    """
    Verifica que el usuario tenga el rol de Product Owner ('PO')
    y sea propietario del tablero al que pertenece la historia.
    """
    # 1. Validar propiedad del tablero
    board_service.get_board_for_user(user, story.board_id)
    
    # 2. Validar rol de Product Owner
    if getattr(user, 'role', 'DEV') != 'PO':
        raise PermissionDenied("Solo el Product Owner puede realizar acciones de aprobación o validación.")

def approve_story(user, story_id):
    """
    Aprueba una historia de usuario tras validar permisos de Product Owner.
    """
    story = get_object_or_404(UserStory, id=story_id)
    validate_po_permissions(user, story)
    
    story.approval_status = 'APPROVED'
    story.approved_by = user
    story.approved_at = timezone.now()
    story.rejection_reason = None
    story.save()
    
    from apps.authentication.services import rbac_service
    rbac_service.log_action(
        user=user,
        action='STORY_APPROVE',
        description=f"Historia de usuario '{story.title}' (ID: {story.id}) aprobada."
    )
    return story

def reject_story(user, story_id, reason):
    """
    Rechaza una historia de usuario especificando un motivo.
    """
    if not reason or not reason.strip():
        raise ValidationError("El motivo de rechazo es obligatorio para rechazar una historia de usuario.")
        
    story = get_object_or_404(UserStory, id=story_id)
    validate_po_permissions(user, story)
    
    story.approval_status = 'REJECTED'
    story.rejection_reason = reason.strip()
    story.approved_by = user
    story.approved_at = timezone.now()
    story.save()
    
    from apps.authentication.services import rbac_service
    rbac_service.log_action(
        user=user,
        action='STORY_REJECT',
        description=f"Historia de usuario '{story.title}' (ID: {story.id}) rechazada. Motivo: {reason.strip()}."
    )
    return story

def request_changes(user, story_id, reason):
    """
    Solicita ajustes para una historia de usuario especificando los detalles del cambio.
    """
    if not reason or not reason.strip():
        raise ValidationError("Debes especificar los cambios solicitados en el motivo.")
        
    story = get_object_or_404(UserStory, id=story_id)
    validate_po_permissions(user, story)
    
    story.approval_status = 'CHANGES_REQUESTED'
    story.rejection_reason = reason.strip()
    story.approved_by = user
    story.approved_at = timezone.now()
    story.save()
    
    from apps.authentication.services import rbac_service
    rbac_service.log_action(
        user=user,
        action='STORY_CHANGES_REQUESTED',
        description=f"Ajustes solicitados para la historia '{story.title}' (ID: {story.id}). Motivo: {reason.strip()}."
    )
    return story
