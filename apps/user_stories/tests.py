import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from apps.boards.services import board_service
from apps.columns.services import column_service
from apps.cards.services import card_service
from apps.user_stories.models import UserStory
from apps.user_stories.services import user_story_service

User = get_user_model()

class UserStoryTests(TestCase):
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
        self.column_other = column_service.create_column(self.board2, "Columna B1")

        # Crear tarjetas de prueba
        self.card1 = card_service.create_card(self.user1, self.column1.id, "Tarea 1")
        self.card_other = card_service.create_card(self.user2, self.column_other.id, "Tarea Ajena")

    def test_create_story_service_success(self):
        """
        Verifica que el servicio cree una historia de usuario correctamente.
        """
        story = user_story_service.create_story(
            self.user1, self.board1.id, "Historia 1", "Como usuario...", 100, "HIGH", "ACTIVE"
        )
        self.assertEqual(story.title, "Historia 1")
        self.assertEqual(story.description, "Como usuario...")
        self.assertEqual(story.business_value, 100)
        self.assertEqual(story.priority, "HIGH")
        self.assertEqual(story.board, self.board1)
        self.assertEqual(story.created_by, self.user1)

    def test_create_story_service_non_owner(self):
        """
        Verifica que un no dueño reciba PermissionDenied al crear.
        """
        with self.assertRaises(PermissionDenied):
            user_story_service.create_story(self.user2, self.board1.id, "Hack Story")

    def test_create_story_service_duplicate_title(self):
        """
        Verifica que se bloquee la creación de títulos duplicados en el mismo tablero.
        """
        user_story_service.create_story(self.user1, self.board1.id, "Historia 1")
        with self.assertRaises(ValidationError) as ctx:
            user_story_service.create_story(self.user1, self.board1.id, "historia 1")
        self.assertIn("Ya existe una historia de usuario llamada 'historia 1' en este tablero.", str(ctx.exception))

    def test_update_story_service_success(self):
        """
        Verifica la actualización de atributos de una historia.
        """
        story = user_story_service.create_story(self.user1, self.board1.id, "Historia Original")
        updated = user_story_service.update_story(
            self.user1, story.id, "Historia Modificada", "Nueva desc", 500, "LOW", "COMPLETED"
        )
        self.assertEqual(updated.title, "Historia Modificada")
        self.assertEqual(updated.description, "Nueva desc")
        self.assertEqual(updated.business_value, 500)
        self.assertEqual(updated.priority, "LOW")
        self.assertEqual(updated.status, "COMPLETED")

    def test_update_story_service_duplicate_title(self):
        """
        Verifica que la actualización bloquee duplicar nombres existentes de otras historias.
        """
        story1 = user_story_service.create_story(self.user1, self.board1.id, "Historia A")
        story2 = user_story_service.create_story(self.user1, self.board1.id, "Historia B")
        with self.assertRaises(ValidationError):
            user_story_service.update_story(self.user1, story2.id, "historia a")

    def test_link_card_same_board(self):
        """
        Verifica la asociación correcta de una tarjeta a una historia del mismo tablero.
        """
        story = user_story_service.create_story(self.user1, self.board1.id, "Story 1")
        card = user_story_service.link_card_to_story(self.user1, self.card1.id, story.id)
        self.assertEqual(card.user_story, story)

    def test_link_card_different_boards(self):
        """
        Verifica que se impida asociar tarjetas a historias de diferentes tableros.
        """
        story = user_story_service.create_story(self.user1, self.board1.id, "Story 1")
        
        # Intento 1: La tarjeta pertenece al tablero 2 (del usuario 2) -> Lanza PermissionDenied por la tarjeta
        with self.assertRaises(PermissionDenied):
            user_story_service.link_card_to_story(self.user1, self.card_other.id, story.id)

        # Intento 2: Usuario 1 es dueño de ambas, pero están en tableros diferentes
        board3 = board_service.create_board(self.user1, "Tablero 3 User 1")
        column_other_u1 = column_service.create_column(board3, "Columna C1")
        card_other_u1 = card_service.create_card(self.user1, column_other_u1.id, "Tarea en Tablero 3")
        with self.assertRaises(ValidationError) as ctx:
            user_story_service.link_card_to_story(self.user1, card_other_u1.id, story.id)
        self.assertIn("No puedes asociar una tarjeta a una historia de usuario de otro tablero.", str(ctx.exception))

    def test_create_story_view_success(self):
        """
        Verifica el endpoint de creación de historias de usuario.
        """
        self.client.login(email='user1@organa.com', password='password123')
        response = self.client.post(
            reverse('create_story'),
            data=json.dumps({
                "board_id": self.board1.id,
                "title": "API Story",
                "description": "Via API",
                "business_value": 200,
                "priority": "HIGH"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['story']['title'], "API Story")
        self.assertEqual(data['story']['business_value'], 200)

    def test_list_stories_view_success(self):
        """
        Verifica el endpoint de listado de historias de un tablero.
        """
        self.client.login(email='user1@organa.com', password='password123')
        user_story_service.create_story(self.user1, self.board1.id, "Story A")
        user_story_service.create_story(self.user1, self.board1.id, "Story B")
        
        response = self.client.get(reverse('list_stories', kwargs={'board_id': self.board1.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['stories']), 2)

    def test_detail_story_view_success(self):
        """
        Verifica el endpoint de detalle de historia de usuario con sus tarjetas vinculadas.
        """
        self.client.login(email='user1@organa.com', password='password123')
        story = user_story_service.create_story(self.user1, self.board1.id, "Story Details")
        user_story_service.link_card_to_story(self.user1, self.card1.id, story.id)

        response = self.client.get(reverse('detail_story', kwargs={'story_id': story.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['story']['title'], "Story Details")
        self.assertEqual(len(data['story']['cards']), 1)
        self.assertEqual(data['story']['cards'][0]['title'], "Tarea 1")

    def test_link_card_view_success(self):
        """
        Verifica el endpoint de vinculación y desvinculación de tarjetas.
        """
        self.client.login(email='user1@organa.com', password='password123')
        story = user_story_service.create_story(self.user1, self.board1.id, "Story Target")
        
        # Vincular
        response = self.client.post(
            reverse('link_card'),
            data=json.dumps({
                "card_id": self.card1.id,
                "story_id": story.id
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.card1.refresh_from_db()
        self.assertEqual(self.card1.user_story, story)

        # Desvincular
        response = self.client.post(
            reverse('link_card'),
            data=json.dumps({
                "card_id": self.card1.id,
                "story_id": None
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.card1.refresh_from_db()
        self.assertNil = self.assertIsNone(self.card1.user_story)
