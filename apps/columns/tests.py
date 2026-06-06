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

    def test_update_column_service_success(self):
        """
        Verifica que el servicio modifique el nombre de la columna.
        """
        col = column_service.create_column(self.board1, "Inicial")
        updated = column_service.update_column(self.user1, col.id, "Modificado")
        self.assertEqual(updated.name, "Modificado")

    def test_update_column_service_duplicate_name(self):
        """
        Verifica que el servicio bloquee cambiar el nombre a uno ya existente en el mismo tablero.
        """
        column_service.create_column(self.board1, "Columna A")
        col = column_service.create_column(self.board1, "Columna B")
        with self.assertRaises(ValidationError):
            column_service.update_column(self.user1, col.id, "columna a")

    def test_update_column_service_non_owner(self):
        """
        Verifica que un no propietario reciba PermissionDenied al actualizar la columna.
        """
        col = column_service.create_column(self.board1, "Columna A")
        with self.assertRaises(PermissionDenied):
            column_service.update_column(self.user2, col.id, "Hack")

    def test_delete_column_service_success(self):
        """
        Verifica que el servicio elimine la columna y normalice las posiciones restantes.
        """
        col1 = column_service.create_column(self.board1, "A") # 1
        col2 = column_service.create_column(self.board1, "B") # 2
        col3 = column_service.create_column(self.board1, "C") # 3
        
        column_service.delete_column(self.user1, col2.id)
        
        self.assertFalse(KanbanColumn.objects.filter(id=col2.id).exists())
        col1.refresh_from_db()
        col3.refresh_from_db()
        
        # Deben normalizarse a 1 y 2
        self.assertEqual(col1.position, 1)
        self.assertEqual(col3.position, 2)

    def test_delete_column_service_non_owner(self):
        """
        Verifica que un no propietario reciba PermissionDenied al eliminar una columna.
        """
        col = column_service.create_column(self.board1, "Eliminame")
        with self.assertRaises(PermissionDenied):
            column_service.delete_column(self.user2, col.id)

    def test_update_column_view_success(self):
        """
        Verifica que la API permita al dueño renombrar la columna.
        """
        self.client.login(email='user1@organa.com', password='password123')
        col = column_service.create_column(self.board1, "Original")
        response = self.client.post(
            reverse('update_column', kwargs={'column_id': col.id}),
            data=json.dumps({"name": "Modificado"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['column']['name'], "Modificado")

    def test_update_column_view_non_owner(self):
        """
        Verifica que la API bloquee con 403 los intentos de actualizar de un no dueño.
        """
        self.client.login(email='user2@organa.com', password='password123')
        col = column_service.create_column(self.board1, "Original")
        response = self.client.post(
            reverse('update_column', kwargs={'column_id': col.id}),
            data=json.dumps({"name": "Hack"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_column_view_success(self):
        """
        Verifica que la API permita al dueño eliminar la columna.
        """
        self.client.login(email='user1@organa.com', password='password123')
        col = column_service.create_column(self.board1, "Eliminame")
        response = self.client.post(reverse('delete_column', kwargs={'column_id': col.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(KanbanColumn.objects.filter(id=col.id).exists())

    def test_delete_column_view_non_owner(self):
        """
        Verifica que la API bloquee con 403 los intentos de eliminar de un no dueño.
        """
        self.client.login(email='user2@organa.com', password='password123')
        col = column_service.create_column(self.board1, "Eliminame")
        response = self.client.post(reverse('delete_column', kwargs={'column_id': col.id}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(KanbanColumn.objects.filter(id=col.id).exists())
