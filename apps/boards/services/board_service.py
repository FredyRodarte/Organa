from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from apps.boards.models import KanbanBoard

def validate_duplicate_board(owner, name):
    """
    Verifica si ya existe un tablero con el mismo nombre para el usuario.
    Lanza un ValidationError en español si se encuentra un duplicado.
    """
    if KanbanBoard.objects.filter(owner=owner, name__iexact=name.strip()).exists():
        raise ValidationError(
            f"Ya tienes un tablero creado con el nombre '{name.strip()}'."
        )

def create_board(owner, name, description=None):
    """
    Valida nombres duplicados y crea una nueva instancia de KanbanBoard.
    """
    if not name or not name.strip():
        raise ValidationError("El nombre del tablero es obligatorio.")
    
    name_clean = name.strip()
    validate_duplicate_board(owner, name_clean)
    
    board = KanbanBoard.objects.create(
        owner=owner,
        name=name_clean,
        description=description.strip() if description else None
    )
    return board

def get_user_boards(owner):
    """
    Obtiene todos los tableros Kanban que pertenecen al usuario dado,
    ordenados del más reciente al más antiguo, optimizando consultas mediante select_related.
    """
    return KanbanBoard.objects.filter(owner=owner).select_related('owner').order_by('-created_at')

def get_board_for_user(user, board_id):
    """
    Obtiene un tablero específico por su ID y valida de forma estricta la propiedad del mismo.
    Si el tablero no existe, lanza un error 404. Si el usuario no es el propietario,
    lanza PermissionDenied (que se traduce en un código HTTP 403 Forbidden).
    """
    board = get_object_or_404(KanbanBoard, id=board_id)
    if board.owner != user:
        raise PermissionDenied("No tienes permisos para acceder a este tablero.")
    return board
