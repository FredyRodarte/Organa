from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from apps.columns.models import KanbanColumn

def validate_column_name(board, name, exclude_column_id=None):
    """
    Valida que el nombre de la columna no esté vacío y no esté duplicado
    (insensible a mayúsculas/minúsculas) dentro del mismo tablero.
    """
    if not name or not name.strip():
        raise ValidationError("El nombre de la columna es obligatorio.")
    
    name_clean = name.strip()
    query = KanbanColumn.objects.filter(board=board, name__iexact=name_clean)
    if exclude_column_id:
        query = query.exclude(id=exclude_column_id)
        
    if query.exists():
        raise ValidationError(f"Ya existe una columna llamada '{name_clean}' en este tablero.")

def create_column(board, name, position=None):
    """
    Valida el nombre y crea una nueva KanbanColumn en el tablero.
    Si no se provee la posición, se le asigna automáticamente la siguiente posición disponible.
    """
    if not name or not name.strip():
        raise ValidationError("El nombre de la columna es obligatorio.")
        
    name_clean = name.strip()
    validate_column_name(board, name_clean)
    
    if position is None:
        # Calcular la siguiente posición disponible (Max + 1)
        max_pos = board.columns.aggregate(max_pos=Max('position'))['max_pos']
        position = (max_pos or 0) + 1
    else:
        # Validar que la posición no esté en uso
        if board.columns.filter(position=position).exists():
            raise ValidationError(f"La posición {position} ya está en uso en este tablero.")
            
    column = KanbanColumn.objects.create(
        board=board,
        name=name_clean,
        position=position
    )
    return column

def get_board_columns(board):
    """
    Retorna las columnas de un tablero ordenadas por posición.
    """
    return board.columns.all()

def reorder_columns(board, column_order_list):
    """
    Reordena las columnas de un tablero usando una lista de IDs de columna ordenados.
    Utiliza una transacción atómica y posiciones temporales para evitar conflictos de UniqueConstraint.
    """
    if not column_order_list:
        return []
        
    # Eliminar duplicados de la lista manteniendo el orden
    seen = set()
    clean_order = [x for x in column_order_list if not (x in seen or seen.add(x))]
    
    with transaction.atomic():
        # Obtener las columnas del tablero que están en la lista para validar pertenencia
        columns = list(board.columns.filter(id__in=clean_order))
        
        if len(columns) != len(clean_order):
            raise ValidationError("Algunas columnas especificadas no existen o no pertenecen a este tablero.")
            
        # 1. Asignar posiciones temporales altas fuera del rango para evitar conflictos únicos
        for col in columns:
            col.position = col.position + 100000
            col.save()
            
        # 2. Asignar las nuevas posiciones finales consecutivas basadas en el orden provisto (1, 2, 3...)
        col_map = {col.id: col for col in columns}
        updated_columns = []
        for index, col_id in enumerate(clean_order, start=1):
            col = col_map[col_id]
            col.position = index
            col.save()
            updated_columns.append(col)
            
        return updated_columns

def get_column_for_user(user, column_id):
    """
    Obtiene una columna Kanban tras verificar la propiedad del tablero al que pertenece.
    Lanza Http404 si la columna no existe, y PermissionDenied si el usuario no es el dueño.
    """
    from django.shortcuts import get_object_or_404
    from apps.boards.services import board_service
    column = get_object_or_404(KanbanColumn, id=column_id)
    # Validar propiedad del tablero
    board_service.get_board_for_user(user, column.board_id)
    return column

def update_column(user, column_id, name):
    """
    Actualiza el nombre de una columna Kanban tras validar ownership y nombre único.
    """
    if not name or not name.strip():
        raise ValidationError("El nombre de la columna es obligatorio.")
        
    name_clean = name.strip()
    column = get_column_for_user(user, column_id)
    
    # Validar que no se duplique el nombre
    validate_column_name(column.board, name_clean, exclude_column_id=column_id)
    
    column.name = name_clean
    column.save()
    return column

def delete_column(user, column_id):
    """
    Elimina una columna Kanban y normaliza la posición del resto de columnas secuencialmente.
    """
    column = get_column_for_user(user, column_id)
    
    with transaction.atomic():
        board = column.board
        column.delete()
        
        # Normalizar posiciones para evitar huecos en la base de datos (1, 2, 3...)
        remaining_columns = board.columns.all().order_by('position')
        for index, col in enumerate(remaining_columns, start=1):
            if col.position != index:
                col.position = index
                col.save()
