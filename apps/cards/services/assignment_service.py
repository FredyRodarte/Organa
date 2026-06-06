from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import Http404
from apps.authentication.models import CustomUser
from apps.cards.models import KanbanCard
from apps.authentication.services import rbac_service

def validate_assignment(operator, card_id, user_id=None):
    """
    Valida que la tarjeta exista, que el usuario de destino exista (si se provee)
    y que el operador tenga permisos de Scrum Master ('manage_flow') y propiedad del tablero.
    """
    card = get_object_or_404(KanbanCard, id=card_id)
    
    # 1. Validar propiedad y permiso por rol Scrum
    rbac_service.authorize_action(operator, 'manage_flow', card)
    
    user = None
    if user_id is not None:
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError(f"El usuario con ID {user_id} no existe en el sistema.")
            
    return card, user

def assign_user(operator, card_id, user_id):
    """
    Asigna un usuario a una tarjeta.
    """
    if not user_id:
        raise ValidationError("El ID del usuario es obligatorio para realizar la asignación.")
        
    card, user = validate_assignment(operator, card_id, user_id)
    
    card.assigned_to = user
    card.assigned_at = timezone.now()
    card.assigned_by = operator
    card.save()
    
    rbac_service.log_action(
        user=operator,
        action='CARD_ASSIGN',
        description=f"Tarjeta '{card.title}' (ID: {card.id}) asignada a {user.email} por {operator.email}."
    )
    return card

def reassign_user(operator, card_id, user_id):
    """
    Reasigna una tarjeta a otro usuario.
    """
    if not user_id:
        raise ValidationError("El ID del usuario es obligatorio para realizar la reasignación.")
        
    card, user = validate_assignment(operator, card_id, user_id)
    
    old_assignee = card.assigned_to
    card.assigned_to = user
    card.assigned_at = timezone.now()
    card.assigned_by = operator
    card.save()
    
    old_email = old_assignee.email if old_assignee else "ninguno"
    rbac_service.log_action(
        user=operator,
        action='CARD_REASSIGN',
        description=f"Tarjeta '{card.title}' (ID: {card.id}) reasignada de {old_email} a {user.email} por {operator.email}."
    )
    return card

def unassign_user(operator, card_id):
    """
    Remueve el usuario asignado de una tarjeta.
    """
    card, _ = validate_assignment(operator, card_id)
    
    old_assignee = card.assigned_to
    if not old_assignee:
        return card # Ya estaba desasignada
        
    card.assigned_to = None
    card.assigned_at = None
    card.assigned_by = None
    card.save()
    
    rbac_service.log_action(
        user=operator,
        action='CARD_UNASSIGN',
        description=f"Tarjeta '{card.title}' (ID: {card.id}) desasignada (anteriormente: {old_assignee.email}) por {operator.email}."
    )
    return card

def get_user_cards(operator, user_id):
    """
    Consulta las tarjetas asignadas a un usuario específico.
    Si el operador es un Developer, sólo puede consultar sus propias tarjetas asignadas.
    Product Owners y Scrum Masters pueden consultar las de cualquier usuario.
    """
    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        raise Http404("El usuario especificado no existe.")
        
    # Superusuarios omiten todas las restricciones
    if not operator.is_superuser:
        if operator.id != target_user.id:
            # Si quiere ver la carga de otro usuario, debe ser PO o SM
            has_po = rbac_service.validate_permission(operator, 'view_metrics')
            has_sm = rbac_service.validate_permission(operator, 'manage_flow')
            if not (has_po or has_sm):
                raise PermissionDenied("No tienes permisos Scrum para consultar la carga de trabajo de otros usuarios.")
                
    return KanbanCard.objects.filter(assigned_to=target_user)
