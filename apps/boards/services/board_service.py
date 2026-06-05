from django.core.exceptions import ValidationError
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
    ordenados del más reciente al más antiguo.
    """
    return KanbanBoard.objects.filter(owner=owner).order_by('-created_at')
