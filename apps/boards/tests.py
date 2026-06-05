import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from apps.boards.models import KanbanBoard
from apps.boards.services import board_service

User = get_user_model()

class KanbanBoardTests(TestCase):
    def setUp(self):
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

    def test_create_board_service(self):
        """
        Verifica que el servicio cree un tablero de manera correcta.
        """
        board = board_service.create_board(self.user1, "Proyecto Organa", "Descripción del proyecto")
        self.assertEqual(board.name, "Proyecto Organa")
        self.assertEqual(board.description, "Descripción del proyecto")
        self.assertEqual(board.owner, self.user1)

    def test_create_duplicate_board_raises_validation_error(self):
        """
        Verifica que el servicio bloquee la creación de tableros duplicados para el mismo usuario (insensible a mayúsculas/minúsculas).
        """
        board_service.create_board(self.user1, "Mi Tablero")
        with self.assertRaises(ValidationError) as ctx:
            board_service.create_board(self.user1, "mi tablero")
        self.assertIn("Ya tienes un tablero creado con el nombre 'mi tablero'", str(ctx.exception))

    def test_allow_same_board_name_different_users(self):
        """
        Verifica que diferentes usuarios puedan crear tableros con el mismo nombre.
        """
        board1 = board_service.create_board(self.user1, "Compartido")
        board2 = board_service.create_board(self.user2, "Compartido")
        self.assertIsNotNone(board1.id)
        self.assertIsNotNone(board2.id)

    def test_get_user_boards_returns_only_owned_boards(self):
        """
        Verifica que el servicio retorne únicamente los tableros del dueño y ordenados del más nuevo al más antiguo.
        """
        b1 = board_service.create_board(self.user1, "Board A")
        b2 = board_service.create_board(self.user1, "Board B")
        board_service.create_board(self.user2, "Board User 2")

        user1_boards = board_service.get_user_boards(self.user1)
        self.assertEqual(len(user1_boards), 2)
        # Orden descendente: el más nuevo (b2) debe aparecer primero
        self.assertEqual(user1_boards[0], b2)
        self.assertEqual(user1_boards[1], b1)

    def test_list_boards_view_unauthenticated(self):
        """
        Verifica que un usuario no autenticado sea redirigido al login al intentar listar tableros.
        """
        response = self.client.get(reverse('list_boards'))
        self.assertEqual(response.status_code, 302)

    def test_create_board_view_unauthenticated(self):
        """
        Verifica que un usuario no autenticado sea redirigido al login al intentar crear un tablero.
        """
        response = self.client.post(
            reverse('create_board'),
            data=json.dumps({"name": "Nuevo"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 302)

    def test_list_boards_view_authenticated(self):
        """
        Verifica que un usuario autenticado pueda listar sus tableros exitosamente.
        """
        # AllAuth está configurado para loguear usando email como credencial primaria
        self.client.login(email='user1@organa.com', password='password123')
        board_service.create_board(self.user1, "Mi Tablero A")
        
        response = self.client.get(reverse('list_boards'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['boards']), 1)
        self.assertEqual(data['boards'][0]['name'], "Mi Tablero A")

    def test_create_board_view_authenticated_success(self):
        """
        Verifica que un usuario autenticado pueda crear un tablero mediante la API.
        """
        self.client.login(email='user1@organa.com', password='password123')
        response = self.client.post(
            reverse('create_board'),
            data=json.dumps({"name": "Tablero Nuevo", "description": "Prueba"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['board']['name'], "Tablero Nuevo")
        self.assertTrue(KanbanBoard.objects.filter(owner=self.user1, name="Tablero Nuevo").exists())

    def test_create_board_view_authenticated_duplicate_error(self):
        """
        Verifica que la API retorne un estado HTTP 400 y mensaje en español al intentar crear un nombre duplicado.
        """
        self.client.login(email='user1@organa.com', password='password123')
        board_service.create_board(self.user1, "Repetido")
        
        response = self.client.post(
            reverse('create_board'),
            data=json.dumps({"name": "Repetido"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], "Ya tienes un tablero creado con el nombre 'Repetido'.")
