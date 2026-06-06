import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from django.shortcuts import get_object_or_404
from apps.boards.services import board_service
from apps.columns.services import column_service
from apps.cards.models import KanbanCard
from apps.cards.services import card_service

User = get_user_model()

class KanbanCardTests(TestCase):
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

        # Crear columnas de prueba
        self.column1 = column_service.create_column(self.board1, "Columna A1")
        self.column2 = column_service.create_column(self.board1, "Columna A2")
        self.column_other = column_service.create_column(self.board2, "Columna B1")

    def test_create_card_service_success(self):
        """
        Verifica que se cree una tarjeta en una columna autorizada correctamente.
        """
        card = card_service.create_card(self.user1, self.column1.id, "Nueva Tarea", "Detalle", "HIGH")
        self.assertEqual(card.title, "Nueva Tarea")
        self.assertEqual(card.description, "Detalle")
        self.assertEqual(card.priority, "HIGH")
        self.assertEqual(card.column, self.column1)

    def test_create_card_service_invalid_priority(self):
        """
        Verifica que no se permita una prioridad inexistente.
        """
        with self.assertRaises(ValidationError):
            card_service.create_card(self.user1, self.column1.id, "Tarea", "Detalle", "SUPER_HIGH")

    def test_create_card_service_empty_title(self):
        """
        Verifica que se obligue a tener un título no vacío.
        """
        with self.assertRaises(ValidationError):
            card_service.create_card(self.user1, self.column1.id, "   ", "Detalle", "MEDIUM")

    def test_create_card_service_non_owner(self):
        """
        Verifica que un usuario sin permisos no pueda crear tarjetas en columnas ajenas.
        """
        with self.assertRaises(PermissionDenied):
            card_service.create_card(self.user2, self.column1.id, "Tarea Intrusiva")

    def test_update_card_service_success(self):
        """
        Verifica que el propietario pueda modificar datos de su tarjeta.
        """
        card = card_service.create_card(self.user1, self.column1.id, "Original")
        updated = card_service.update_card(self.user1, card.id, "Modificado", "Nueva Desc", "LOW")
        self.assertEqual(updated.title, "Modificado")
        self.assertEqual(updated.description, "Nueva Desc")
        self.assertEqual(updated.priority, "LOW")

    def test_update_card_service_non_owner(self):
        """
        Verifica que un no propietario no pueda editar la tarjeta.
        """
        card = card_service.create_card(self.user1, self.column1.id, "Original")
        with self.assertRaises(PermissionDenied):
            card_service.update_card(self.user2, card.id, "Hackeo")

    def test_move_card_service_success(self):
        """
        Verifica que se pueda mover una tarjeta a otra columna del mismo tablero.
        """
        card = card_service.create_card(self.user1, self.column1.id, "A mover")
        moved = card_service.move_card(self.user1, card.id, self.column2.id)
        self.assertEqual(moved.column, self.column2)

    def test_move_card_service_different_boards(self):
        """
        Verifica que se impida mover tarjetas entre columnas de distintos tableros.
        """
        card = card_service.create_card(self.user1, self.column1.id, "A mover")
        
        # Caso 1: Columna destino pertenece a otro usuario (debe lanzar PermissionDenied)
        with self.assertRaises(PermissionDenied):
            card_service.move_card(self.user1, card.id, self.column_other.id)
            
        # Caso 2: Columna destino pertenece al mismo usuario pero a otro tablero (debe lanzar ValidationError)
        board3 = board_service.create_board(self.user1, "Tablero 3 User 1", "Desc 3")
        column_other_user1 = column_service.create_column(board3, "Columna C1")
        with self.assertRaises(ValidationError):
            card_service.move_card(self.user1, card.id, column_other_user1.id)

    def test_delete_card_service_success(self):
        """
        Verifica la eliminación correcta de una tarjeta por su dueño.
        """
        card = card_service.create_card(self.user1, self.column1.id, "A borrar")
        card_id = card.id
        card_service.delete_card(self.user1, card_id)
        self.assertFalse(KanbanCard.objects.filter(id=card_id).exists())

    def test_delete_card_service_non_owner(self):
        """
        Verifica que un no dueño reciba PermissionDenied al intentar borrar.
        """
        card = card_service.create_card(self.user1, self.column1.id, "A borrar")
        with self.assertRaises(PermissionDenied):
            card_service.delete_card(self.user2, card.id)

    def test_create_card_view_success(self):
        """
        Verifica el endpoint de creación de tarjetas.
        """
        self.client.login(email='user1@organa.com', password='password123')
        response = self.client.post(
            reverse('create_card'),
            data=json.dumps({
                "column_id": self.column1.id,
                "title": "API Card",
                "description": "Via endpoint",
                "priority": "HIGH"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['card']['title'], "API Card")
        self.assertEqual(data['card']['column_id'], self.column1.id)

    def test_create_card_view_non_owner(self):
        """
        Verifica que el endpoint de creación bloquee con 403 a usuarios no dueños.
        """
        self.client.login(email='user2@organa.com', password='password123')
        response = self.client.post(
            reverse('create_card'),
            data=json.dumps({
                "column_id": self.column1.id,
                "title": "API Hack"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_update_card_view_success(self):
        """
        Verifica el endpoint de actualización de tarjetas.
        """
        self.client.login(email='user1@organa.com', password='password123')
        card = card_service.create_card(self.user1, self.column1.id, "Original Title")
        response = self.client.post(
            reverse('update_card'),
            data=json.dumps({
                "card_id": card.id,
                "title": "Updated Title",
                "description": "Updated description",
                "priority": "LOW"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['card']['title'], "Updated Title")
        self.assertEqual(data['card']['column_id'], self.column1.id)

    def test_move_card_view_success(self):
        """
        Verifica el endpoint de mover tarjetas.
        """
        self.client.login(email='user1@organa.com', password='password123')
        card = card_service.create_card(self.user1, self.column1.id, "Mover API")
        response = self.client.post(
            reverse('move_card'),
            data=json.dumps({
                "card_id": card.id,
                "target_column_id": self.column2.id
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        card.refresh_from_db()
        self.assertEqual(card.column, self.column2)

    def test_delete_card_view_success(self):
        """
        Verifica el endpoint de eliminar tarjetas.
        """
        self.client.login(email='user1@organa.com', password='password123')
        card = card_service.create_card(self.user1, self.column1.id, "Borrar API")
        response = self.client.post(
            reverse('delete_card'),
            data=json.dumps({
                "card_id": card.id
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(KanbanCard.objects.filter(id=card.id).exists())

    def test_list_cards_view_success(self):
        """
        Verifica el endpoint de listar tarjetas de una columna.
        """
        self.client.login(email='user1@organa.com', password='password123')
        card_service.create_card(self.user1, self.column1.id, "Card 1")
        card_service.create_card(self.user1, self.column1.id, "Card 2")

        response = self.client.get(reverse('list_cards', kwargs={'column_id': self.column1.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['cards']), 2)
        self.assertEqual(data['cards'][0]['title'], "Card 1")
        self.assertEqual(data['cards'][0]['column_id'], self.column1.id)
        self.assertEqual(data['cards'][1]['title'], "Card 2")
        self.assertEqual(data['cards'][1]['column_id'], self.column1.id)
