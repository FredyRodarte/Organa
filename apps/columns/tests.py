import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from apps.boards.models import KanbanBoard
from apps.boards.services import board_service
from apps.columns.models import KanbanColumn
from apps.columns.services import column_service

User = get_user_model()

class KanbanColumnTests(TestCase):
    def setUp(self):
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(
            username='user1@organa.com',
            email='user1@organa.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2@organa.com',
            email='user2@organa.com',
            password='password123'
        )
        
        # Crear tableros de prueba
        self.board1 = board_service.create_board(self.user1, "Tablero User 1", "Desc 1")
        self.board2 = board_service.create_board(self.user2, "Tablero User 2", "Desc 2")

    def test_create_column_service_success(self):
        """
        Verifica que el servicio cree una columna correctamente y auto-asigne la posición 1.
        """
        col = column_service.create_column(self.board1, "Por Hacer")
        self.assertEqual(col.name, "Por Hacer")
        self.assertEqual(col.position, 1)
        self.assertEqual(col.board, self.board1)

    def test_create_column_service_auto_positioning(self):
        """
        Verifica que se asigne secuencialmente la posición correcta (Max + 1) al crear varias columnas.
        """
        col1 = column_service.create_column(self.board1, "Columna 1")
        col2 = column_service.create_column(self.board1, "Columna 2")
        col3 = column_service.create_column(self.board1, "Columna 3")
        
        self.assertEqual(col1.position, 1)
        self.assertEqual(col2.position, 2)
        self.assertEqual(col3.position, 3)

    def test_create_column_service_duplicate_name(self):
        """
        Verifica que no se permita crear columnas duplicadas (case-insensitive) dentro del mismo tablero.
        """
        column_service.create_column(self.board1, "Por Hacer")
        with self.assertRaises(ValidationError) as ctx:
            column_service.create_column(self.board1, "por hacer")
        self.assertIn("Ya existe una columna llamada 'por hacer'", str(ctx.exception))

    def test_create_column_service_allow_same_name_different_boards(self):
        """
        Verifica que se permita crear columnas con el mismo nombre en diferentes tableros.
        """
        col1 = column_service.create_column(self.board1, "Por Hacer")
        col2 = column_service.create_column(self.board2, "Por Hacer")
        self.assertIsNotNone(col1.id)
        self.assertIsNotNone(col2.id)

    def test_reorder_columns_service_success(self):
        """
        Verifica que el servicio reordene las columnas correctamente y asigne posiciones estables.
        """
        col1 = column_service.create_column(self.board1, "A") # pos: 1
        col2 = column_service.create_column(self.board1, "B") # pos: 2
        col3 = column_service.create_column(self.board1, "C") # pos: 3
        
        # Nuevo orden: col3, col1, col2
        column_service.reorder_columns(self.board1, [col3.id, col1.id, col2.id])
        
        # Recargar columnas de la base de datos
        col1.refresh_from_db()
        col2.refresh_from_db()
        col3.refresh_from_db()
        
        self.assertEqual(col3.position, 1)
        self.assertEqual(col1.position, 2)
        self.assertEqual(col2.position, 3)

    def test_reorder_columns_service_foreign_board(self):
        """
        Verifica que reordenar con una columna ajena al tablero lance una excepción de validación.
        """
        col1 = column_service.create_column(self.board1, "Col A")
        col2_other = column_service.create_column(self.board2, "Col Other")
        
        with self.assertRaises(ValidationError):
            column_service.reorder_columns(self.board1, [col1.id, col2_other.id])

    def test_create_column_view_authenticated_owner(self):
        """
        Verifica que el propietario autenticado pueda crear columnas mediante la API.
        """
        self.client.login(email='user1@organa.com', password='password123')
        response = self.client.post(
            reverse('create_column'),
            data=json.dumps({"board_id": self.board1.id, "name": "Backlog"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['column']['name'], "Backlog")
        self.assertTrue(KanbanColumn.objects.filter(board=self.board1, name="Backlog").exists())

    def test_create_column_view_authenticated_non_owner(self):
        """
        Verifica que un usuario autenticado que no es el propietario reciba HTTP 403.
        """
        self.client.login(email='user2@organa.com', password='password123')
        response = self.client.post(
            reverse('create_column'),
            data=json.dumps({"board_id": self.board1.id, "name": "Hack"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(KanbanColumn.objects.filter(board=self.board1, name="Hack").exists())

    def test_list_columns_view_success(self):
        """
        Verifica que el propietario pueda listar sus columnas correctamente.
        """
        self.client.login(email='user1@organa.com', password='password123')
        column_service.create_column(self.board1, "Col A")
        column_service.create_column(self.board1, "Col B")
        
        response = self.client.get(reverse('list_board_columns', kwargs={'board_id': self.board1.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['columns']), 2)
        self.assertEqual(data['columns'][0]['name'], "Col A")
        self.assertEqual(data['columns'][1]['name'], "Col B")

    def test_list_columns_view_non_owner(self):
        """
        Verifica que un no propietario reciba HTTP 403 al listar columnas.
        """
        self.client.login(email='user2@organa.com', password='password123')
        response = self.client.get(reverse('list_board_columns', kwargs={'board_id': self.board1.id}))
        self.assertEqual(response.status_code, 403)

    def test_reorder_columns_view_success(self):
        """
        Verifica que el propietario pueda reordenar columnas mediante la API.
        """
        self.client.login(email='user1@organa.com', password='password123')
        c1 = column_service.create_column(self.board1, "A")
        c2 = column_service.create_column(self.board1, "B")
        
        response = self.client.post(
            reverse('reorder_columns'),
            data=json.dumps({"board_id": self.board1.id, "column_ids": [c2.id, c1.id]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        # Validar en la base de datos
        c1.refresh_from_db()
        c2.refresh_from_db()
        self.assertEqual(c2.position, 1)
        self.assertEqual(c1.position, 2)

    def test_reorder_columns_view_non_owner(self):
        """
        Verifica que un no propietario reciba HTTP 403 al reordenar columnas.
        """
        self.client.login(email='user2@organa.com', password='password123')
        c1 = column_service.create_column(self.board1, "A")
        c2 = column_service.create_column(self.board1, "B")
        
        response = self.client.post(
            reverse('reorder_columns'),
            data=json.dumps({"board_id": self.board1.id, "column_ids": [c2.id, c1.id]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
