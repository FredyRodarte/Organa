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
from apps.cards.services import card_movement_service

User = get_user_model()

class KanbanCardMovementTests(TestCase):
    def setUp(self):
        # Crear usuarios de prueba
        self.user_owner = User.objects.create_user(
            username='owner@organa.com',
            email='owner@organa.com',
            password='password123'
        )
        self.user_hacker = User.objects.create_user(
            username='hacker@organa.com',
            email='hacker@organa.com',
            password='password123'
        )
        
        # Crear tableros
        self.board_owner = board_service.create_board(self.user_owner, "Tablero Owner", "Desc")
        self.board_hacker = board_service.create_board(self.user_hacker, "Tablero Hacker", "Desc")

        # Crear columnas para el dueño
        self.col_a = column_service.create_column(self.board_owner, "Columna A")
        self.col_b = column_service.create_column(self.board_owner, "Columna B")
        
        # Crear columnas para el hacker
        self.col_hacker = column_service.create_column(self.board_hacker, "Columna Hacker")

        # Crear tarjetas en la columna A
        self.card_a1 = card_service.create_card(self.user_owner, self.col_a.id, "Tarea A1") # pos: 0
        self.card_a2 = card_service.create_card(self.user_owner, self.col_a.id, "Tarea A2") # pos: 1
        self.card_a3 = card_service.create_card(self.user_owner, self.col_a.id, "Tarea A3") # pos: 2

    def test_initial_positions(self):
        """
        Verifica que al crear las tarjetas se les asigne una posición secuencial empezando desde 0.
        """
        c1 = KanbanCard.objects.get(id=self.card_a1.id)
        c2 = KanbanCard.objects.get(id=self.card_a2.id)
        c3 = KanbanCard.objects.get(id=self.card_a3.id)
        self.assertEqual(c1.position, 0)
        self.assertEqual(c2.position, 1)
        self.assertEqual(c3.position, 2)

    def test_reorder_within_same_column(self):
        """
        Mueve la tarjeta A3 (pos 2) a la posición 0 dentro de la misma columna A.
        """
        card_movement_service.move_card(
            self.user_owner,
            self.card_a3.id,
            self.col_a.id,
            self.col_a.id,
            0
        )
        
        # Re-obtener en orden de posición
        cards = list(self.col_a.cards.all().order_by('position'))
        self.assertEqual(cards[0].id, self.card_a3.id)
        self.assertEqual(cards[0].position, 0)
        
        self.assertEqual(cards[1].id, self.card_a1.id)
        self.assertEqual(cards[1].position, 1)
        
        self.assertEqual(cards[2].id, self.card_a2.id)
        self.assertEqual(cards[2].position, 2)

    def test_move_to_different_column(self):
        """
        Mueve la tarjeta A2 (pos 1 de col_a) a la columna B en la posición 0.
        """
        # Crear una tarjeta en columna B previa
        card_b1 = card_service.create_card(self.user_owner, self.col_b.id, "Tarea B1") # pos: 0
        
        card_movement_service.move_card(
            self.user_owner,
            self.card_a2.id,
            self.col_a.id,
            self.col_b.id,
            0
        )
        
        # Verificar columna A (debería quedar con A1 en pos 0 y A3 en pos 1)
        cards_a = list(self.col_a.cards.all().order_by('position'))
        self.assertEqual(len(cards_a), 2)
        self.assertEqual(cards_a[0].id, self.card_a1.id)
        self.assertEqual(cards_a[0].position, 0)
        self.assertEqual(cards_a[1].id, self.card_a3.id)
        self.assertEqual(cards_a[1].position, 1)
        
        # Verificar columna B (debería tener A2 en pos 0 y B1 en pos 1)
        cards_b = list(self.col_b.cards.all().order_by('position'))
        self.assertEqual(len(cards_b), 2)
        self.assertEqual(cards_b[0].id, self.card_a2.id)
        self.assertEqual(cards_b[0].position, 0)
        self.assertEqual(cards_b[1].id, card_b1.id)
        self.assertEqual(cards_b[1].position, 1)

    def test_move_card_invalid_source_column(self):
        """
        Verifica que se lance una validación si la columna origen indicada no es la actual.
        """
        with self.assertRaises(ValidationError):
            card_movement_service.move_card(
                self.user_owner,
                self.card_a1.id,
                self.col_b.id, # Columna origen incorrecta
                self.col_b.id,
                0
            )

    def test_move_card_to_hacker_board_forbidden(self):
        """
        Verifica que se lance PermissionDenied si se intenta mover a una columna de otro usuario.
        """
        with self.assertRaises(PermissionDenied):
            card_movement_service.move_card(
                self.user_owner,
                self.card_a1.id,
                self.col_a.id,
                self.col_hacker.id,
                0
            )

    def test_move_card_different_boards_same_owner_forbidden(self):
        """
        Verifica que se lance ValidationError si se intenta mover una tarjeta
        a otro tablero diferente propiedad del mismo usuario.
        """
        # Crear otro tablero del mismo dueño
        board_other = board_service.create_board(self.user_owner, "Otro Tablero Owner", "Desc")
        col_other_board = column_service.create_column(board_other, "Columna en otro tablero")
        
        with self.assertRaises(ValidationError):
            card_movement_service.move_card(
                self.user_owner,
                self.card_a1.id,
                self.col_a.id,
                col_other_board.id,
                0
            )

    def test_move_card_unauthorized(self):
        """
        Verifica que un usuario ajeno al tablero no pueda mover tarjetas.
        """
        with self.assertRaises(PermissionDenied):
            card_movement_service.move_card(
                self.user_hacker,
                self.card_a1.id,
                self.col_a.id,
                self.col_b.id,
                0
            )

    def test_reorder_on_deletion(self):
        """
        Verifica que al eliminar una tarjeta intermedia (A2), las restantes (A1, A3)
        recalculen sus posiciones para quedar consecutivas (0, 1).
        """
        card_service.delete_card(self.user_owner, self.card_a2.id)
        
        cards = list(self.col_a.cards.all().order_by('position'))
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0].id, self.card_a1.id)
        self.assertEqual(cards[0].position, 0)
        self.assertEqual(cards[1].id, self.card_a3.id)
        self.assertEqual(cards[1].position, 1)

    def test_move_card_view_api_success(self):
        """
        Verifica el endpoint API /cards/move mediante POST/PUT.
        """
        self.client.force_login(self.user_owner)
        url = reverse('move_card')
        payload = {
            'card_id': self.card_a2.id,
            'source_column': self.col_a.id,
            'target_column': self.col_b.id,
            'position': 0
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['card']['column_id'], self.col_b.id)
        self.assertEqual(data['card']['position'], 0)
