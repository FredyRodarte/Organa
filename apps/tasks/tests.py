import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import Http404
from django.urls import reverse
from apps.boards.services import board_service
from apps.user_stories.services import user_story_service
from apps.tasks.services import task_service
from apps.tasks.models import TechnicalTask

User = get_user_model()

class TechnicalTaskServiceTests(TestCase):
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

        # Crear historias de prueba
        self.story1 = user_story_service.create_story(self.user1, self.board1.id, "Story 1")
        self.story2 = user_story_service.create_story(self.user2, self.board2.id, "Story 2")

    def test_create_task_success(self):
        """
        Verifica que se cree una tarea técnica correctamente en la capa de servicios.
        """
        task = task_service.create_task(
            self.user1, self.story1.id, "Tarea Técnica A", "Descripción A", 5, "TODO"
        )
        self.assertEqual(task.title, "Tarea Técnica A")
        self.assertEqual(task.description, "Descripción A")
        self.assertEqual(task.estimated_hours, 5)
        self.assertEqual(task.status, "TODO")
        self.assertEqual(task.user_story, self.story1)

    def test_create_task_non_owner(self):
        """
        Verifica que un usuario que no es dueño reciba PermissionDenied.
        """
        with self.assertRaises(PermissionDenied):
            task_service.create_task(
                self.user2, self.story1.id, "Hack Task", "", 1, "TODO"
            )

    def test_create_task_duplicate_title(self):
        """
        Verifica que no se puedan crear dos tareas con el mismo título (insensible a mayúsculas) en la misma historia.
        """
        task_service.create_task(self.user1, self.story1.id, "Tarea A")
        with self.assertRaises(ValidationError) as ctx:
            task_service.create_task(self.user1, self.story1.id, "tarea a")
        self.assertIn("Ya existe una tarea llamada 'tarea a' en esta historia de usuario.", str(ctx.exception))

    def test_create_task_invalid_hours(self):
        """
        Verifica que se lance un ValidationError si las horas estimadas son negativas.
        """
        with self.assertRaises(ValidationError) as ctx:
            task_service.create_task(self.user1, self.story1.id, "Tarea Invalida", "", -2)
        self.assertIn("Las horas estimadas deben ser un número entero positivo o cero.", str(ctx.exception))

    def test_update_task_success(self):
        """
        Verifica que se pueda actualizar una tarea correctamente.
        """
        task = task_service.create_task(self.user1, self.story1.id, "Tarea Original", "", 3, "TODO")
        updated = task_service.update_task(
            self.user1, task.id, "Tarea Modificada", "Nueva Desc", 8, "IN_PROGRESS"
        )
        self.assertEqual(updated.title, "Tarea Modificada")
        self.assertEqual(updated.description, "Nueva Desc")
        self.assertEqual(updated.estimated_hours, 8)
        self.assertEqual(updated.status, "IN_PROGRESS")

    def test_update_task_duplicate_title(self):
        """
        Verifica que la actualización lance ValidationError si se duplica un título existente en otra tarea de la misma historia.
        """
        task_service.create_task(self.user1, self.story1.id, "Tarea X")
        task2 = task_service.create_task(self.user1, self.story1.id, "Tarea Y")
        with self.assertRaises(ValidationError):
            task_service.update_task(self.user1, task2.id, "tarea x")

    def test_delete_task_success(self):
        """
        Verifica que se pueda eliminar una tarea.
        """
        task = task_service.create_task(self.user1, self.story1.id, "Tarea a eliminar")
        task_id = task.id
        deleted_id = task_service.delete_task(self.user1, task_id)
        self.assertEqual(deleted_id, task_id)
        self.assertFalse(TechnicalTask.objects.filter(id=task_id).exists())

    def test_cascade_delete_behavior(self):
        """
        Verifica que al eliminar la historia de usuario se eliminen sus tareas técnicas en cascada.
        """
        task = task_service.create_task(self.user1, self.story1.id, "Subtarea de Story 1")
        self.assertTrue(TechnicalTask.objects.filter(id=task.id).exists())
        self.story1.delete()
        self.assertFalse(TechnicalTask.objects.filter(id=task.id).exists())


class TechnicalTaskAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user@organa.com',
            email='user@organa.com',
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='other@organa.com',
            email='other@organa.com',
            password='password123'
        )
        self.board = board_service.create_board(self.user, "Tablero")
        self.story = user_story_service.create_story(self.user, self.board.id, "Story principal")
        self.client.login(email='user@organa.com', password='password123')

    def test_create_task_view_success(self):
        """
        Verifica el endpoint de creación de tareas técnicas.
        """
        response = self.client.post(
            reverse('create_task'),
            data=json.dumps({
                "story_id": self.story.id,
                "title": "Subtarea API",
                "description": "Creada por API",
                "estimated_hours": 4,
                "status": "TODO"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['task']['title'], "Subtarea API")

    def test_create_task_view_invalid_data(self):
        """
        Verifica que el endpoint devuelva 400 con datos incorrectos.
        """
        response = self.client.post(
            reverse('create_task'),
            data=json.dumps({
                "story_id": self.story.id,
                "title": "",
                "estimated_hours": -5
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')

    def test_update_task_view_success(self):
        """
        Verifica la modificación de una tarea técnica mediante API.
        """
        task = task_service.create_task(self.user, self.story.id, "Tarea API")
        response = self.client.post(
            reverse('update_task'),
            data=json.dumps({
                "task_id": task.id,
                "title": "Tarea API Modificada",
                "estimated_hours": 10,
                "status": "IN_PROGRESS"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['task']['title'], "Tarea API Modificada")
        self.assertEqual(data['task']['status'], "IN_PROGRESS")

    def test_list_tasks_view_success(self):
        """
        Verifica que se listen correctamente las tareas técnicas de una historia.
        """
        task_service.create_task(self.user, self.story.id, "Tarea A")
        task_service.create_task(self.user, self.story.id, "Tarea B")
        
        response = self.client.get(reverse('list_tasks', kwargs={'story_id': self.story.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['tasks']), 2)

    def test_delete_task_view_success(self):
        """
        Verifica la eliminación de una tarea técnica mediante API.
        """
        task = task_service.create_task(self.user, self.story.id, "A borrar")
        response = self.client.post(
            reverse('delete_task'),
            data=json.dumps({
                "task_id": task.id
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(TechnicalTask.objects.filter(id=task.id).exists())
